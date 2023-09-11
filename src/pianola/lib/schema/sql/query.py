from dataclasses import dataclass
from typing import Union

from pianola.lib.schema.sql.table import Table
from pianola.lib.schema.sql.view import View


@dataclass
class Query:
    name: str
    sql: str
    one: bool
