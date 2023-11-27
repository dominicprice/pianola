from typing import Callable
from urllib.parse import ParseResult, urlparse

import pianola.analyse.sqlite as sqlite
from pianola.analyse import whoosh
from pianola.lib.schema import Schema

analysers: dict[str, Callable[[ParseResult], Schema]] = {
    "sqlite": sqlite.analyse,
    "sqlite3": sqlite.analyse,
    "whoosh": whoosh.analyse,
}


def analyse(uri: str) -> Schema:
    parsed_uri = urlparse(uri)
    analyser = analysers.get(parsed_uri.scheme)
    if analyser is None:
        raise RuntimeError("unknown database scheme " + parsed_uri.scheme)

    return analyser(parsed_uri)
