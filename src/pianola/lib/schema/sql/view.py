from dataclasses import dataclass
from typing import Optional

from pianola.lib.schema.sql.column import Column
from pianola.lib.schema.sql.table import Table
from pianola.lib.stringutils import quote


@dataclass
class ColumnInfo:
    table: Table
    alias: Optional[str]


@dataclass
class View:
    sqlname: str
    pyname: str
    quoted: bool
    columns: list[Column]
    column_info: list[ColumnInfo]

    def find_column(self, name: str, quoted: bool) -> Column:
        for column in self.columns:
            if column.sqlname == name and column.quoted == quoted:
                return column

        q = '"' if quoted else ""
        raise KeyError("column " + quote(name, q) + " does not exist")
