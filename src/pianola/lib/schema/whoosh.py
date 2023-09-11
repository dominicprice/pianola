from dataclasses import dataclass

from pianola.lib.schema import Schema

import whoosh.index as index


@dataclass
class WhooshSchema(Schema):
    indices: list[index.FileIndex]
