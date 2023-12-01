from pathlib import Path

from pianola.generate.sqlite.query import generate_query
from pianola.lib.schema.sql.column import Column
from pianola.lib.schema.sql.query import Query
from pianola.lib.schema.sql.view import View
from pianola.lib.stringutils import quote, sql_to_module_name
from pianola.lib.writer import Writer


def generate_view(view: View, outdir: Path, package_name: str):
    generator = ViewGenerator(view, outdir, package_name)
    generator.generate()


class ViewGenerator:
    def __init__(self, view: View, outdir: Path, package_name: str):
        self.view = view
        self.outdir = outdir
        self.package_name = package_name
        self.sqlname = quote(view.sqlname, '"' if view.quoted else "")

    def generate(self):
        filename = sql_to_module_name(self.view.sqlname) + ".py"
        with Writer(self.outdir / filename) as w:
            self.generate_header(w)
            self.generate_class_header(w)
            with w.indented():
                self.generate_query(w)

    def generate_header(self, w: Writer):
        w.writeline(
            "from ",
            self.package_name,
            ".utils import _UNSET",
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
        w.writeline("from typing import Union, Optional, Any, Generator, TYPE_CHECKING")
        w.writeline("from datetime import date, datetime, time")
        w.writeline("from decimal import Decimal")
        w.writeline("if TYPE_CHECKING:")
        with w.indented():
            w.writeline("from _typeshed.dbapi import DBAPICursor")
        w.writeline()

    def generate_class_header(self, w: Writer):
        w.writeline("class ", self.view.pyname, ":")
        with w.indented():
            w.writeline(
                "def __init__(self, ",
                ", ".join(f"{f.pyname}: {f.pytype}" for f in self.view.columns),
                "):",
            )
            with w.indented():
                for field in self.view.columns:
                    w.writeline(
                        "self.",
                        field.pyname,
                        ": ",
                        field.pytype,
                        " = ",
                        field.pyname,
                    )
            w.writeline()

    def generate_query(self, w: Writer):
        def query_sql(col: Column):
            return (
                "SELECT "
                + ", ".join(c.sqlname for c in self.view.columns)
                + " WHERE "
                + col.sqlname
                + " = {"
                + col.pyname
                + " "
                + col.pytype
                + "}"
            )

        for col in self.view.columns:
            name = "by_" + col.pyname
            sql = query_sql(col)
            generate_query(w, self.view, Query(name, sql, False))
