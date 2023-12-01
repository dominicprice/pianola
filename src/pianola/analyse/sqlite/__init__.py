import sqlite3
from urllib.parse import ParseResult

from pianola.analyse.sqlite.index import schema_populate_indices
from pianola.analyse.sqlite.table import schema_populate_tables
from pianola.analyse.sqlite.views import schema_populate_views
from pianola.lib.schema.sql import SqlSchema


def analyse(filename: ParseResult) -> SqlSchema:
    schema = SqlSchema(dialect="sqlite", tables=[], views=[])
    with sqlite3.connect(filename.path) as conn:
        cursor = conn.cursor()
        schema_populate_tables(schema, cursor)
        schema_populate_indices(schema, cursor)
        schema_populate_views(schema, cursor)
    return schema
