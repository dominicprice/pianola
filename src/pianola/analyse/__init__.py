from typing import Callable
from urllib.parse import urlparse

import pianola.analyse.sqlite as sqlite
from pianola.lib.schema import Schema

analysers: dict[str, Callable[[str], Schema]] = {
    "sqlite": sqlite.analyse,
    "sqlite3": sqlite.analyse,
}


def anaylse(uri: str) -> Schema:
    parsed_uri = urlparse(uri)
    analyser = analysers.get(parsed_uri.scheme)
    if analyser is None:
        raise RuntimeError("unknown database scheme " + parsed_uri.scheme)

    return analyser(parsed_uri.path)
