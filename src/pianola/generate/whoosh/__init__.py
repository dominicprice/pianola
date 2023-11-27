from pathlib import Path

from pianola.generate.whoosh.index import IndexGenerator
from pianola.lib.schema.whoosh import WhooshSchema
from pianola.lib.writer import Writer


def generate(
    schema: WhooshSchema,
    outdir: Path,
    package_name: str,
    exclude: list[str] = [],
):
    outdir.mkdir(exist_ok=True)

    pkgs: dict[str, list[str]] = {}
    for idx in schema.indices:
        if idx.indexname in exclude:
            continue

        g = IndexGenerator(idx, outdir)
        pkgs[idx.indexname] = g.generate()

    with Writer(outdir / "__init__.py") as w:
        for pkg, classes in pkgs.items():
            w.writeline("from ", package_name, ".", pkg, " import ", ", ".join(classes))
