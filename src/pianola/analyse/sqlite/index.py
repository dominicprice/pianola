import sqlite3

from pianola.lib.pytypes.sql import INTEGER_TYPES
from pianola.lib.schema.sql import Index, SqlSchema, Table


def table_populate_index(
    table: Table, index_name: str, unique: bool, cursor: sqlite3.Cursor
):
    index = Index(index_name, [], unique)
    cursor.execute(f"PRAGMA index_info({index_name})")
    idx_rows = cursor.fetchall()
    for _, _, name in idx_rows:
        column = table.find_column(name, False)
        index.columns += [column]
    table.indices += [index]


def schema_populate_indices(schema: SqlSchema, cursor: sqlite3.Cursor):
    for table in schema.tables:
        cursor.execute(f"PRAGMA INDEX_LIST('{table.sqlname}')")
        rows = cursor.fetchall()
        for seq, name, unique, origin, partial in rows:
            table_populate_index(table, name, unique, cursor)

    # rowid primary keys do not get an explicit index created
    for table in schema.tables:
        pks = [column for column in table.columns if column.primary_key]
        pk_index_exists = False
        for index in table.indices:
            if pks == index.columns:
                pk_index_exists = True
                break

        if not pk_index_exists and len(pks) == 1 and pks[0].sqltype in INTEGER_TYPES:
            table.indices += [Index("pianola_implicit_rowid_index", pks, True)]
