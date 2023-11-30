from dataclasses import dataclass

from pianola.lib.schema.sql.column import Column


@dataclass
class Index:
    name: str
    columns: list[Column]
    unique: bool
