from pathlib import Path
from typing import Any, Callable

import pianola.generate.sqlite as sqlite
from pianola.lib.schema import Schema

generators: dict[str, Callable[[Any, Path, str, list[str]], None]] = {
    "sqlite": sqlite.generate
}


def generate(schema: Schema, outdir: Path, package_name: str, exclude: list[str] = []):
    generator = generators.get(schema.dialect)
    if generator is None:
        raise RuntimeError("unknown schema dialect " + schema.dialect)

    return generator(schema, outdir, package_name, exclude)
