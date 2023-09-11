from typing import IO, Union

import inflect
import stringcase

import whoosh.index as index
from whoosh.fields import (
    BOOLEAN,
    DATETIME,
    ID,
    KEYWORD,
    NUMERIC,
    STORED,
    TEXT,
    FieldType,
)


def field_type(field_obj: FieldType):
    if isinstance(field_obj, BOOLEAN):
        return "bool"
    elif isinstance(field_obj, DATETIME):
        return "datetime"
    elif isinstance(field_obj, ID):
        return "str"
    elif isinstance(field_obj, TEXT):
        return "str"
    elif isinstance(field_obj, KEYWORD):
        return "list[str]"
    elif isinstance(field_obj, NUMERIC):
        return "float"
    elif isinstance(field_obj, STORED):
        return "Any"
    else:
        t = type(field_obj)
        raise ValueError(f"{t} is not a valid type")


class IndexGenerator:
    def __init__(self, idx: index.FileIndex, f: IO[str]):
        self.f = f
        self.index = idx
        self.all_fields = []
        self.stored_fields = []
        self.unstored_fields = []
        for name, obj in self.index.schema.items():
            try:
                python_type = field_type(obj)
            except ValueError as e:
                raise ValueError(f"field {name} is invalid: {e}")

            field = (name, python_type, obj.unique)
            self.all_fields += [field]
            if obj.stored:
                self.stored_fields += [field]
            else:
                self.unstored_fields += [field]

        i = inflect.engine()
        indexname = self.index.indexname
        if s := i.singular_noun(indexname):
            indexname = s
        self.basename = stringcase.pascalcase(indexname)

    def generate(self):
        self.generate_imports()
        types = self.generate_types()
        entry = self.generate_entry()
        result = self.generate_result()
        return types + entry + result

    def generate_imports(self):
        self.import_from("datetime", "datetime")
        self.import_from("typing", "Any", "Optional", "Union")
        self.import_from("whoosh.writing", "IndexWriter")
        self.import_from("whoosh.searching", "Searcher")
        self.import_from("whoosh.query", "Query")
        self.import_from("dataclasses", "dataclass", "asdict")

    def generate_types(self) -> list[str]:
        self.f.write(
            self.basename
            + 'Type = Union["'
            + self.basename
            + 'Entry", "'
            + self.basename
            + 'Result"]\n'
        )
        return [self.basename + "Type"]

    def generate_entry(self) -> list[str]:
        self.decorator("dataclass")
        self.class_def(self.basename + "Entry")
        for field in self.all_fields:
            self.class_var(field[0], field[1], True)

        self.class_method(
            "insert",
            ["w: IndexWriter"],
            None,
            "w.add_document(**self.asdict())",
        )

        self.class_method("asdict", [], ("dict", "str", "Any"), "return asdict(self)")

        return [self.basename + "Entry"]

    def generate_result(self) -> list[str]:
        self.decorator("dataclass", "frozen=True")
        self.class_def(self.basename + "Result")
        for field in self.stored_fields:
            self.class_var(field[0], field[1], True)

        self.class_static_method(
            "query",
            ["s: Searcher", "query: Query", "limit: Optional[int] = 10"],
            ("list", self.basename + "Result"),
            "results = s.search(query, limit=limit)",
            f"return [{self.basename}Result(**res) for res in results]",
        )

        self.class_static_method(
            "query_one",
            ["s: Searcher", "query: Query"],
            ("Optional", self.basename + "Result"),
            "results = s.search(query, limit=1)",
            "if len(results) == 0:",
            "    return None",
            f"return {self.basename}Result(**results[0])",
        )

        self.class_static_method(
            "query_page",
            ["s: Searcher", "query: Query", "page: int", "page_size: int = 10"],
            ("list", self.basename + "Result"),
            "results = s.search_page(query, page, pagelen=page_size)",
            f"return [{self.basename}Result(**res) for res in results]",
        )

        self.class_method(
            "to_entry",
            [],
            self.basename + "Entry",
            f"return {self.basename}Entry(**asdict(self))",
        )

        return [self.basename + "Result"]

    def import_from(self, module: str, *exports: str):
        self.f.write(f"from {module} import {', '.join(exports)}\n")

    def class_var(self, name: str, typ: str, optional: bool):
        if optional:
            typ = "Optional[" + typ + "] = None"
        self.f.write("    " + name + ": " + typ + "\n")

    def class_def(self, name: str, *super_classes: str):
        self.f.write(f"class {name}")
        if super_classes:
            self.f.write("(" + ", ".join(super_classes) + ")")
        self.f.write(":\n")

    def return_type(self, t: Union[str, tuple[str, ...], None]):
        if isinstance(t, str):
            self.f.write(" -> '" + t + "'")
        elif isinstance(t, tuple):
            type_origin, *type_args = t
            self.f.write(" -> '" + type_origin + "[" + ", ".join(type_args) + "]'")

    def class_static_method(
        self,
        name: str,
        args: list[str],
        return_type: Union[str, tuple[str, ...], None],
        *body: str,
    ):
        self.f.write(f"    @staticmethod\n")
        self.f.write(f"    def {name}(" + ", ".join(args) + ")")
        self.return_type(return_type)
        self.f.write(":")
        self.f.writelines("\n        " + line for line in body)
        self.f.write("\n\n")

    def class_method(
        self,
        name: str,
        args: list[str],
        return_type: Union[str, tuple[str, ...], None],
        *body: str,
    ):
        self.f.write(f"    def {name}(" + ", ".join(["self"] + args) + ")")
        self.return_type(return_type)
        self.f.write(":")
        self.f.writelines("\n        " + line for line in body)
        self.f.write("\n\n")

    def decorator(self, name: str, *args: str):
        self.f.write("@" + name)
        if args:
            self.f.write("(" + ", ".join(a for a in args) + ")")
        self.f.write("\n")
