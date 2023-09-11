import sqlglot.expressions as exp
import stringcase as sc
from pianola.analyse.sqlite.utils import resolve_reference
from pianola.lib.pytypes.sql import col_add_pytype
from pianola.lib.schema.sql import Column, SqlSchema


def column_populate_constraints(
    column: Column,
    constraints: exp.ColumnConstraint,
    schema: SqlSchema,
):
    for _, con in constraints.iter_expressions():
        if isinstance(con, exp.PrimaryKeyColumnConstraint):
            column.primary_key = True
        elif isinstance(con, exp.NotNullColumnConstraint):
            column.nullable = False
        elif isinstance(con, exp.Reference):
            reference_col = resolve_reference(con, schema)
            column.reference = reference_col
        elif isinstance(con, exp.DefaultColumnConstraint):
            if con.this is None:
                raise ValueError("default has no 'this' value")
            assert isinstance(con.this, exp.Literal)
            value = con.this.this
            assert isinstance(value, str)
            if con.this.is_string:
                column.default_value = value
            elif con.this.is_int:
                column.default_value = int(value)
            else:
                column.default_value = float(value)
        elif isinstance(con, exp.AutoIncrementColumnConstraint):
            pass
        else:
            raise ValueError(f"unknown column constraint {con}")


def column_from_expr(column: exp.ColumnDef, schema: SqlSchema) -> Column:
    res = Column()
    for _, expr in column.iter_expressions():
        if isinstance(expr, exp.Identifier):
            assert isinstance(expr.this, str)
            res.sqlname = expr.this
            res.pyname = sc.snakecase(res.sqlname)
            res.quoted = expr.quoted
        elif isinstance(expr, exp.DataType):
            assert isinstance(expr.this, exp.DataType.Type)
            res.sqltype = expr.this.value
        elif isinstance(expr, exp.ColumnConstraint):
            column_populate_constraints(res, expr, schema)
        else:
            raise ValueError(f"unknown column expression {expr}")
    try:
        col_add_pytype(res)
    except Exception as e:
        raise RuntimeError("column " + res.sqlname + ": " + str(e))
    return res
