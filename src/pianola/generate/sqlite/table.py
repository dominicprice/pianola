import os
import re
from pathlib import Path
from typing import Optional

from pianola.generate.sqlite.query import generate_query
from pianola.lib.schema.sql import Column, Query, Table
from pianola.lib.stringutils import quote, sql_to_module_name
from pianola.lib.writer import Writer

ALLOWED_TYPES = ["int", "float", "str", "bytes"]
ALLOWED_TYPES += ["Optional[" + t + "]" for t in ALLOWED_TYPES]


def generate_table(
    table: Table,
    outdir: Path,
    package_name: str,
    queries: list[Query],
):
    generator = TableGenerator(table, outdir, package_name, queries)
    generator.generate()


def get_and_replace_param(param: str, params: list[tuple[str, str]]):
    ident, typ = param.split()
    if not ident.isidentifier():
        raise ValueError("param is not a valid python identifier")
    if typ not in ALLOWED_TYPES:
        raise ValueError("param is not of a valid python type")
    params += [(ident, typ)]
    return "?"


class TableGenerator:
    def __init__(
        self, table: Table, outdir: Path, package_name: str, queries: list[Query]
    ):
        self.table = table
        self.outdir = outdir
        self.package_name = package_name
        self.sqlname = quote(table.sqlname, '"' if table.quoted else "")
        self.queries = self.index_queries() + queries

    def index_queries(self) -> list[Query]:
        queries: list[Query] = []
        cols = ", ".join(c.sqlname for c in self.table.columns)
        for index in self.table.indices:
            name = "by_" + "_".join(c.pyname for c in index.columns)
            where = " AND ".join(
                f"{c.sqlname} = {{{c.pyname} {c.pytype}}}" for c in index.columns
            )
            queries += [
                Query(
                    name,
                    "SELECT "
                    + cols
                    + " FROM "
                    + self.table.sqlname
                    + " WHERE "
                    + where,
                    True,
                ),
            ]
        queries += [
            Query(
                "get",
                "SELECT " + cols + " FROM " + self.table.sqlname,
                False,
            )
        ]
        return queries

    def generate(self):
        filename = sql_to_module_name(self.table.sqlname) + ".py"
        with Writer(self.outdir / filename) as w:
            self.generate_header(w)
            self.generate_class_header(w)
            with w.indented():
                for field in self.table.columns:
                    self.generate_field_property(w, field)
                self.generate_insert(w)
                self.generate_delete(w)
                for query in self.queries:
                    generate_query(w, self.table, query)

    def generate_header(self, w: Writer):
        w.writeline(
            "from ",
            self.package_name,
            ".utils import _UNSET, Cursor, DatabaseError, try_execute",
        )
        w.writeline(
            "from ",
            self.package_name,
            ".converters import ",
            "datetime_to_sql, ",
            "datetime_from_sql, ",
            "optional_datetime_to_sql, ",
            "optional_datetime_from_sql, ",
            "date_to_sql, ",
            "date_from_sql, ",
            "optional_date_to_sql, ",
            "optional_date_from_sql, ",
            "time_to_sql, ",
            "time_from_sql, ",
            "optional_time_to_sql, ",
            "optional_time_from_sql, ",
            "decimal_to_sql, ",
            "decimal_from_sql, ",
            "optional_decimal_to_sql, ",
            "optional_decimal_from_sql",
        )
        w.writeline("from typing import Union, Optional, Any, Generator")
        w.writeline("from datetime import date, datetime, time")
        w.writeline("from decimal import Decimal")
        w.writeline()

    def generate_class_header(self, w: Writer):
        w.writeline("class ", self.table.pyname, ":")
        with w.indented():
            w.writeline(
                "def __init__(self, ",
                ", ".join(
                    f"{f.pyname}: Union[{f.pytype}, _UNSET] = _UNSET()"
                    for f in self.table.columns
                ),
                "):",
            )
            with w.indented():
                for field in self.table.columns:
                    w.writeline(
                        "self._",
                        field.pyname,
                        ": Union[",
                        field.pytype,
                        ", _UNSET] = ",
                        field.pyname,
                    )
            w.writeline()

    def generate_field_property(self, w: Writer, field: Column):
        w.writeline("@property")
        w.writeline("def ", field.pyname, "(self) -> ", field.pytype, ":")
        with w.indented():
            w.writeline("if isinstance(self._", field.pyname, ", _UNSET):")
            with w.indented():
                w.writeline("raise ValueError('", field.pyname, " is unset')")
            w.writeline("return self._", field.pyname)
        w.writeline("@", field.pyname, ".setter")
        w.writeline("def ", field.pyname, "(self, t: ", field.pytype, "):")
        with w.indented():
            w.writeline("self._", field.pyname, " = t")
        w.writeline()

    def generate_set_cols(self, w: Writer, colsname: str, valsname: Optional[str]):
        w.writeline(colsname, ": list[str] = []")
        if valsname:
            w.writeline(valsname, ": list[Any] = []")
        for field in self.table.columns:
            w.writeline("if not isinstance(self._", field.pyname, ", _UNSET):")
            with w.indented():
                w.writeline(colsname, " += ['", field.sqlname, "']")
                if valsname:
                    w.writeline(
                        valsname,
                        " += [",
                        field.val_to_sql("self._" + field.pyname),
                        "]",
                    )

    def generate_insert(self, w: Writer):
        w.writeline("def insert(self, cursor: Cursor):")
        with w.indented():
            self.generate_set_cols(w, "cols", "values")
            w.writeline()
            w.writeline("if cols:")
            with w.indented():
                w.writeline(
                    "stmt = 'INSERT INTO ",
                    self.table.sqlname,
                    "(' + ', '.join(cols) + ') VALUES (' + ', '.join('?' for _ in values) + ') RETURNING ",
                    ", ".join(c.sqlname for c in self.table.columns),
                    "'",
                )
            w.writeline("else:")
            with w.indented():
                w.writeline(
                    "stmt = 'INSERT INTO ",
                    self.table.sqlname,
                    " DEFAULT VALUES RETURNING ",
                    ", ".join(c.sqlname for c in self.table.columns),
                    "'",
                )
            w.writeline("try_execute(cursor, stmt, values)")
            w.writeline("row = cursor.fetchone()")
            w.writeline("if row is None:")
            with w.indented():
                w.writeline(
                    "raise DatabaseError('inserted row did not return any data')"
                )
            for i, column in enumerate(self.table.columns):
                w.writeline(
                    "self._",
                    column.pyname,
                    " = ",
                    column.val_from_sql(f"row[{i}]"),
                )
        w.writeline()

    def generate_delete(self, w: Writer):
        w.writeline("def delete(self, cursor: Cursor):")
        with w.indented():
            pks = [f for f in self.table.columns if f.primary_key]
            w.writeline(
                "stmt = 'DELETE FROM ",
                self.table.sqlname,
                " WHERE ",
                " AND ".join(f"{f.sqlname} = ?" for f in pks),
                "'",
            )
            w.writeline(
                "try_execute(cursor, stmt, [",
                ", ".join(f"self._{f.pyname}" for f in pks),
                "])",
            )
        w.writeline()
