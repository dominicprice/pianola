import argparse
from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass
class Args:
    uri: str = ""


def parse_args(argv: Optional[Sequence[str]] = None) -> Args:
    parser = argparse.ArgumentParser(
        prog="pianola",
        description="Automated code generation for databases",
    )
    parser.add_argument(
        "uri",
        help="scheme qualified database uri (e.g. sqlite://db.sqlite, whoosh://path/to/indices)",
    )

    args = Args()
    parser.parse_args(argv, args)
    return args


def main(args: Args):
    pass
