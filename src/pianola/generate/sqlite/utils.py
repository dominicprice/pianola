from pathlib import Path

from pianola.lib.writer import Writer


def generate_utils(outdir: Path):
    with Writer(outdir / "utils.py") as w:
        w.writeline("from typing import Any, Sequence, Union, Mapping, Protocol")
        w.writeline()

        w.writeline("class _UNSET:")
        with w.indented():
            w.writeline("pass")
        w.writeline()

        w.writeline("class NoRowsError(RuntimeError):")
        with w.indented():
            w.writeline("pass")
