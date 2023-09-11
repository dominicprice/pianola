from dataclasses import dataclass

from pianola.lib.schema.sql.column import Column
from pianola.lib.schema.sql.index import Index
from pianola.lib.stringutils import quote


@dataclass
class Table:
    sqlname: str
    pyname: str
    quoted: bool
    columns: list[Column]
    indices: list[Index]

    def find_column(self, name: str, quoted: bool) -> Column:
        for column in self.columns:
            if column.sqlname == name and column.quoted == quoted:
                return column

        q = '"' if quoted else ""
        raise KeyError("column " + quote(name, q) + " does not exist")

    def find_index(self, name: str) -> Index:
        for index in self.indices:
            if index.name == name:
                return index

        raise KeyError("index " + name + " does not exist")
