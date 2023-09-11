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
    pkgs: dict[str, list[str]] = {}
    for idx in schema.indices:
        if idx.indexname in exclude:
            continue

        with open(outdir / (idx.indexname + ".py"), "w") as f:
            g = IndexGenerator(idx, f)
            pkgs[idx.indexname] = g.generate()

    with Writer(outdir / "__init__.py") as w:
        for pkg, classes in pkgs.items():
            w.writeline("from ", package_name, ".", pkg, " import ", ", ".join(classes))
