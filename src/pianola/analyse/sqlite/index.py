import sqlite3

from pianola.lib.pytypes.sql import INTEGER_TYPES
from pianola.lib.schema.sql import Index, SqlSchema, Table


def table_populate_index(table: Table, index_name: str, cursor: sqlite3.Cursor):
    index = Index(index_name, [])
    cursor.execute(f"PRAGMA index_info({index_name})")
    idx_rows = cursor.fetchall()
    for _, _, name in idx_rows:
        column = table.find_column(name, False)
        index.columns += [column]
    table.indices += [index]


def schema_populate_indices(schema: SqlSchema, cursor: sqlite3.Cursor):
    cursor.execute("SELECT * FROM 'sqlite_master'")
    cursor.execute("SELECT name, tbl_name FROM 'sqlite_master' WHERE type='index'")
    rows = cursor.fetchall()
    for idx_name, tbl_name in rows:
        table = schema.find_table(tbl_name, False)
        table_populate_index(table, idx_name, cursor)

    # rowid primary keys do not get an explicit index created
    for table in schema.tables:
        pks = [column for column in table.columns if column.primary_key]
        if len(pks) == 1 and pks[0].sqltype in INTEGER_TYPES:
            table.indices += [Index("pianola_implicit_rowid_index", pks)]
