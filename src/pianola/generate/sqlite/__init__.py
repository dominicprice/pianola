from pathlib import Path

from pianola.generate.sqlite.converters import generate_converters
from pianola.generate.sqlite.table import generate_table
from pianola.generate.sqlite.utils import generate_utils
from pianola.lib.schema.sql import SqlSchema
from pianola.lib.stringutils import sql_to_class_name, sql_to_module_name
from pianola.lib.writer import Writer


def generate(
    schema: SqlSchema,
    outdir: Path,
    package_name: str,
    exclude_tables: list[str] = [],
):
    outdir.mkdir(exist_ok=True)

    # generate static files
    generate_converters(outdir)
    generate_utils(outdir)

    # generate tables
    generated_tables: list[str] = []
    for table in schema.tables:
        if table.sqlname not in exclude_tables:
            generate_table(table, outdir, package_name, [])
            generated_tables += [table.sqlname]

    # generate module level imports
    with Writer(outdir / "__init__.py") as w:
        for table in generated_tables:
            w.writeline(
                "from ",
                package_name,
                ".",
                sql_to_module_name(table),
                " import ",
                sql_to_class_name(table),
            )
