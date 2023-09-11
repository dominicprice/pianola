from pathlib import Path

from pianola.lib.writer import Writer


def generate_utils(outdir: Path):
    with Writer(outdir / "utils.py") as w:
        w.writeline("from typing import Any, Sequence, Union, Mapping, Protocol")
        w.writeline()

        w.writeline("class Cursor(Protocol):")
        with w.indented():
            w.writeline(
                "def execute(self, stmt: str, ",
                "params: Union[Sequence[Any], Mapping[str, Any]] = ..., /) -> object: ...",
            )
            w.writeline("def fetchone(self) -> Union[Sequence[Any], ", "None]: ...")
            w.writeline(
                "def fetchmany(self, size: int = ...) -> ",
                "Sequence[Sequence[Any]]: ...",
            )
            w.writeline("def fetchall(self) -> Sequence[Sequence[Any]]: ...")
        w.writeline()

        w.writeline("class DatabaseError(RuntimeError):")
        with w.indented():
            w.writeline("pass")
        w.writeline()

        w.writeline("class _UNSET:")
        with w.indented():
            w.writeline("pass")
        w.writeline()

        w.writeline(
            "def try_execute(cursor: Cursor, stmt: str, params: Union[Sequence[Any], Mapping[str, Any]]):"
        )
        with w.indented():
            w.writeline("try:")
            with w.indented():
                w.writeline("cursor.execute(stmt, params)")
            w.writeline("except Exception as e:")
            with w.indented():
                w.writeline(
                    "raise DatabaseError(type(e).__name__",
                    " + ' error executing statement `' + stmt + '`: ' + str(e))",
                )
