import re
from typing import Union

import sqlglot
import sqlglot.expressions as exp
from pianola.lib.schema.sql.column import Column
from pianola.lib.schema.sql.query import Query
from pianola.lib.schema.sql.table import Table
from pianola.lib.schema.sql.view import View
from pianola.lib.writer import Writer


def query_select_cols(sql: str, target: Union[Table, View]) -> list[Column]:
    select = sqlglot.parse_one(sql)
    res = []
    assert isinstance(select, exp.Select)
    for _, expr in select.iter_expressions():
        if isinstance(expr, exp.Column):
            ident = expr.find(exp.Identifier)
            assert ident is not None
            res += [target.find_column(ident.name, ident.quoted)]
        elif isinstance(select, exp.Star):
            return target.columns
        else:
            break
    return res


def query_replace_params(sql: str):
    params: list[tuple[str, str]] = []

    def replace(m: re.Match[str]) -> str:
        nonlocal params
        params += [(m[1], m[2])]
        return "?"

    sql = re.sub(r"\{([^\s]+)\s+([^\}]+)\}", replace, sql)
    return sql, params


def generate_query(w: Writer, target: Union[Table, View], query: Query):
    sql, params = query_replace_params(query.sql)

    if query.one:
        ret = "Optional['" + target.pyname + "']"
    else:
        ret = "Generator['" + target.pyname + "', None, None]"

    w.writeline("@staticmethod")
    w.writeline(
        "def ",
        query.name,
        "(cursor: 'DBAPICursor', ",
        ", ".join(f"{n}: {t}" for n, t in params),
        ") -> ",
        ret,
        ":",
    )

    cols = query_select_cols(sql, target)
    with w.indented():
        fields: list[str] = []
        for i, col in enumerate(cols):
            f = next(c for c in target.columns if c.sqlname == col.sqlname)
            fields += [f.pyname + " = " + f.val_from_sql(f"res[{i}]")]
        w.writeline("stmt = '''" + sql + "'''")
        w.writeline(
            "cursor.execute(stmt, [",
            ", ".join(p[0] for p in params),
            "])",
        )
        if query.one:
            w.writeline("res = cursor.fetchone()")
            w.writeline("if res is None:")
            with w.indented():
                w.writeline("return None")
            w.writeline(
                "return ",
                target.pyname,
                "(",
                ", ".join(fields),
                ")",
            )
        else:
            w.writeline("while res := cursor.fetchone():")
            with w.indented():
                w.writeline(
                    "yield ",
                    target.pyname,
                    "(",
                    ", ".join(fields),
                    ")",
                )
    w.writeline()
