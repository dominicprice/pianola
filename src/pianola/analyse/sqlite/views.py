import sqlite3
from contextlib import contextmanager
from typing import Generator, Type, TypeVar

import sqlglot
import sqlglot.expressions as exp
from pianola.analyse.sqlite.utils import debug_expr
from pianola.lib.schema.sql.schema import SqlSchema
from pianola.lib.schema.sql.view import ColumnInfo, View
from pianola.lib.stringutils import sql_to_class_name

E = TypeVar("E", bound=exp.Expression)


class ExpressionParser:
    def __init__(self, root: exp.Expression):
        self.expressions = list(root.iter_expressions())
        self.idx = 0

    @contextmanager
    def expect_one(self, e: Type[E]) -> Generator[E, None, None]:
        print("expecting ", e)
        if self.idx >= len(self.expressions):
            raise ValueError(f"expected {e}, reached end of expression")
        _, expression = self.expressions[self.idx]
        if not isinstance(expression, e):
            raise ValueError(f"expected {e}, got {type(expression)}")
        self.idx += 1
        yield expression

    @contextmanager
    def expect_one_of(self, *es: Type[E]) -> Generator[exp.Expression, None, None]:
        if self.idx >= len(self.expressions):
            raise ValueError(
                f"expected {' or '.join(e.__name__ for e in es)}, reached end of expression"
            )
        _, expression = self.expressions[self.idx]
        if not any(isinstance(expression, e) for e in es):
            raise ValueError(
                f"expected {' or '.join(e.__name__ for e in es)}, got {type(expression)}"
            )
        self.idx += 1
        yield expression

    def expect_maybe(self, e: Type[E]) -> Generator[E, None, None]:
        if self.idx >= len(self.expressions):
            return
        _, expression = self.expressions[self.idx]
        if not isinstance(expression, e):
            return
        self.idx += 1
        yield expression

    def expect_many(self, e: Type[E]) -> Generator[E, None, None]:
        while self.idx < len(self.expressions):
            _, expression = self.expressions[self.idx]
            if not isinstance(expression, e):
                break
            self.idx += 1
            yield expression

    def expect_many_of(
        self, *e: Type[exp.Expression]
    ) -> Generator[exp.Expression, None, None]:
        while self.idx < len(self.expressions):
            _, expression = self.expressions[self.idx]
            if not any(isinstance(expression, ee) for ee in e):
                break
            self.idx += 1
            yield expression


def populate_column(view: View, column: exp.Column, schema: SqlSchema):
    p = ExpressionParser(column)
    with p.expect_one(exp.Identifier) as ident:
        name = ident.name
        quoted = ident.quoted
    with p.expect_one(exp.Identifier) as ident:
        tbl_name = ident.name
        tbl_quoted = ident.quoted
    table = schema.find_table(tbl_name, tbl_quoted)
    view.columns.append(table.find_column(name, quoted))
    view.column_info.append(ColumnInfo(table, None))


def parse_view(schema: SqlSchema, e: exp.Expression) -> View:
    view = View("", "", False, [], [])
    parser = ExpressionParser(e)
    with parser.expect_one(exp.Table) as ident:
        p = ExpressionParser(ident)
        with p.expect_one(exp.Identifier) as ident:
            view.sqlname = ident.name
            view.pyname = sql_to_class_name(ident.name)
            view.quoted = ident.quoted

    with parser.expect_one(exp.Select) as select:
        p = ExpressionParser(select)
        for column in p.expect_many_of(exp.Column, exp.Alias):
            if isinstance(column, exp.Column):
                populate_column(view, column, schema)
            elif isinstance(column, exp.Alias):
                pp = ExpressionParser(column)
                with pp.expect_one(exp.Column) as col:
                    populate_column(view, col, schema)
                with pp.expect_one(exp.Identifier) as ident:
                    view.column_info[-1].alias = ident.name

    return view


def schema_populate_views(schema: SqlSchema, cursor: sqlite3.Cursor):
    cursor.execute("SELECT name, sql FROM 'sqlite_master' WHERE type='view'")
    rows = cursor.fetchall()
    for _, sql in rows:
        root = sqlglot.parse_one(sql, read="sqlite")
        debug_expr("root", root)
        view = parse_view(schema, root)
        schema.views.append(view)
