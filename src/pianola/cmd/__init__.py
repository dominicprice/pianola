from pathlib import Path

import click
from pianola.analyse import analyse
from pianola.generate import generate


@click.command
@click.option(
    "-p",
    "--package",
    default="models",
    help="Name of the output package",
)
@click.option(
    "-x",
    "--exclude",
    multiple=True,
    default=[],
    help="Tables to exclude from generated code",
)
@click.argument(
    "uri",
    type=str,
)
@click.argument(
    "outdir",
    type=click.Path(path_type=Path),
)
def main(uri: str, outdir: Path, package: str, exclude: list[str]):
    """
    Generate models for the database at URI in the directory OUTDIR. URI should
    be a scheme qualified database uri (e.g. sqlite://db.sqlite,
    whoosh://path/to/indices).
    """
    schema = analyse(uri)
    generate(schema, outdir, package, exclude)
