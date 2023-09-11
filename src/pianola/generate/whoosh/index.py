from pathlib import Path

from pianola.lib.stringutils import sql_to_class_name, sql_to_module_name
from pianola.lib.writer import Writer

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
    def __init__(self, idx: index.FileIndex, outdir: Path):
        self.idx = idx
        self.outdir = outdir
        self.all_fields = []
        self.stored_fields = []
        self.unstored_fields = []
        for name, obj in self.idx.schema.items():
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

        self.basename = sql_to_class_name(self.idx.indexname)

    def generate(self) -> list[str]:
        module = sql_to_module_name(self.idx.indexname)
        classes = []
        with Writer(self.outdir / (module + ".py")) as w:
            self.generate_imports(w)
            classes += self.generate_query(w)
            classes += self.generate_insert(w)
        return classes

    def generate_imports(self, w: Writer):
        w.writeline("from datetime import datetime")
        w.writeline("from typing import Any, Generator, Optional")
        w.writeline("from whoosh.writing import IndexWriter")
        w.writeline("from whoosh.searching import Searcher")
        w.writeline("from whoosh.query import Query")
        w.writeline("from dataclasses import dataclass, asdict")
        w.writeline()

    def generate_query(self, w: Writer) -> list[str]:
        w.writeline("@dataclass")
        w.writeline("class ", self.basename, ":")
        with w.indented():
            for field in self.unstored_fields:
                w.writeline(field[0], ": Optional[", field[1], "] = None")
            w.writeline()

            w.writeline("def for_insert(self) -> '", self.basename, "ForInsert':")
            with w.indented():
                w.writeline("return ", self.basename, "ForInsert(**self.asdict())")
            w.writeline()

            w.writeline("@staticmethod")
            w.writeline(
                "def query(s: Searcher, query: Query, ",
                "limit: Optional[int] = 10) -> Generator['",
                self.basename,
                "', None, None]:",
            )
            with w.indented():
                w.writeline("for res in s.search(query, limit=limit):")
                with w.indented():
                    w.writeline("yield ", self.basename, "(**res)")
            w.writeline()

            w.writeline("@staticmethod")
            w.writeline(
                "def query_one(s: Searcher, query: Query) -> Optional['",
                self.basename,
                "']:",
            )
            with w.indented():
                w.writeline("results = s.search(query, limit=1)")
                w.writeline("if len(results) == 0:")
                with w.indented():
                    w.writeline("return None")
                w.writeline("return ", self.basename, "(**results[0])")
            w.writeline()

            w.writeline("@staticmethod")
            w.writeline(
                "def query_page(s: Searcher, query: Query, ",
                "page: int, page_size: int = 10) -> Generator['",
                self.basename,
                "', None, None]:",
            )
            with w.indented():
                w.writeline("for res in s.search_page(query, page, pagelen=page_size):")
                with w.indented():
                    w.writeline("yield ", self.basename, "(**res)")
            w.writeline()

            w.writeline("def asdict(self) -> dict[str, Any]:")
            with w.indented():
                w.writeline("return asdict(self)")
        w.writeline()

        return [self.basename]

    def generate_insert(self, w: Writer) -> list[str]:
        w.writeline("@dataclass")
        w.writeline("class " + self.basename, "ForInsert(", self.basename, "):")
        with w.indented():
            for field in self.stored_fields:
                w.writeline(field[0], ": Optional[", field[1], "] = None")
            w.writeline()

            w.writeline("def insert(self, w: IndexWriter) -> None:")
            with w.indented():
                w.writeline("w.add_document(**self.asdict())")
            w.writeline()
        w.writeline()

        return [self.basename + "ForInsert"]
