from contextlib import contextmanager
from pathlib import Path
from typing import IO, Any, Union


class Writer:
    def __init__(self, path: Union[str, Path], indent: str = "    "):
        self.f = open(path, "w")
        self.indent_level = 0
        self.indent_str = indent

    def write(self, *args: Any):
        for arg in args:
            self.f.write(str(arg))

    def writeline(self, *args: Any):
        self.f.write(self.indent_str * self.indent_level)
        self.write(*args)
        self.write("\n")

    def indent(self):
        self.indent_level += 1

    def dedent(self):
        self.indent_level -= 1

    def __enter__(self) -> "Writer":
        self.f._checkClosed()
        return self

    def __exit__(self, *_):
        self.f.close()

    @contextmanager
    def indented(self):
        self.indent()
        yield None
        self.dedent()
