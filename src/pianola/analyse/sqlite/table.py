import sqlite3

import sqlglot
import sqlglot.expressions as exp
from pianola.analyse.sqlite.column import column_from_expr
from pianola.analyse.sqlite.utils import resolve_reference
from pianola.lib.schema.sql import SqlSchema, Table
from pianola.lib.stringutils import sql_to_class_name


def schema_populate_table(schema: SqlSchema, table_schema: exp.Schema):
    table = Table("", "", False, [], [])
    for _, expr in table_schema.iter_expressions():
        if isinstance(expr, exp.Table):
            ident = expr.find(exp.Identifier)
            if ident is None:
                raise ValueError("table has no identifier")
            assert isinstance(ident.this, str)
            table.sqlname = ident.this
            table.pyname = sql_to_class_name(ident.this)
            table.quoted = ident.quoted
        elif isinstance(expr, exp.ColumnDef):
            column = column_from_expr(expr, schema)
            table.columns += [column]
        elif isinstance(expr, exp.PrimaryKey):
            for _, pk in expr.iter_expressions():
                assert isinstance(pk.this, str)
                column = table.find_column(pk.this, False)
                column.primary_key = True
        elif isinstance(expr, exp.ForeignKey):
            ident = expr.find(exp.Identifier)
            if ident is None:
                raise ValueError("foreign key has no identifier")
            assert isinstance(ident.this, str)
            reference = expr.find(exp.Reference)
            if reference is None:
                raise ValueError("foreign key has no reference")
            reference_col = resolve_reference(reference, schema)
            table.find_column(ident.this, ident.quoted).reference = reference_col
        elif isinstance(expr, exp.UniqueColumnConstraint):
            pass
        else:
            raise ValueError(f"unknown expression `{expr}` in table schema")

    schema.tables += [table]


def schema_populate_tables(schema: SqlSchema, cursor: sqlite3.Cursor):
    cursor.execute("SELECT name, sql FROM 'sqlite_master' where type='table'")
    rows = cursor.fetchall()
    for name, sql in rows:
        if name.startswith("sqlite_"):
            continue
        root = sqlglot.parse_one(sql, read="sqlite")
        table_schema = root.find(exp.Schema)
        if table_schema is None:
            raise RuntimeError("no table in sql expression")
        schema_populate_table(schema, table_schema)
