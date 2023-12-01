from dataclasses import dataclass

from pianola.lib.schema import Schema
from pianola.lib.schema.sql.table import Table
from pianola.lib.schema.sql.view import View
from pianola.lib.stringutils import quote


@dataclass
class SqlSchema(Schema):
    tables: list[Table]
    views: list[View]

    def find_table(self, name: str, quoted: bool) -> Table:
        for table in self.tables:
            if table.sqlname == name and table.quoted == quoted:
                return table

        q = '"' if quoted else ""
        raise KeyError("table " + quote(name, q) + " does not exist")
