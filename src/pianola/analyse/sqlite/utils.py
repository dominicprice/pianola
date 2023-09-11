from typing import Optional

import sqlglot.expressions as exp
from pianola.lib.schema.sql import Column, SqlSchema, Table


def resolve_reference(reference: exp.Reference, schema: SqlSchema) -> Column:
    ref_schema = reference.find(exp.Schema)
    if ref_schema is None:
        raise ValueError("reference has no schema")

    table: Optional[Table] = None
    for _, expr in ref_schema.iter_expressions():
        if isinstance(expr, exp.Table):
            ident = expr.find(exp.Identifier)
            if ident is None:
                raise ValueError("reference table has no identifier")
            assert isinstance(ident.this, str)
            table = schema.find_table(ident.this, ident.quoted)
        elif isinstance(expr, exp.Identifier):
            if table is None:
                raise RuntimeError("reference column has no associated table")
            assert isinstance(expr.this, str)
            return table.find_column(expr.this, expr.quoted)
    raise RuntimeError("could not resolve reference")
