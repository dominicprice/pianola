import os
import sys
from pathlib import Path
from typing import Generator

import pytest
import whoosh.index as index
from pianola.analyse.whoosh import analyse
from pianola.generate.whoosh import generate
from whoosh.fields import (
    BOOLEAN,
    DATETIME,
    ID,
    KEYWORD,
    NUMERIC,
    STORED,
    TEXT,
    SchemaClass,
)


@pytest.fixture
def indices(tmp_path: Path) -> Generator[Path, None, None]:
    class ABitOfEverythingSchema(SchemaClass):
        boolean = BOOLEAN()
        boolean_stored = BOOLEAN(stored=True)
        datetime = DATETIME()
        datetime_stored = DATETIME(stored=True)
        id = ID()
        id_stored = ID(stored=True)
        keyword = KEYWORD()
        keyword_stored = KEYWORD(stored=True)
        numeric = NUMERIC()
        numeric_stored = NUMERIC(stored=True)
        stored = STORED()
        text = TEXT()
        text_stored = TEXT(stored=True)

    index.create_in(tmp_path, ABitOfEverythingSchema, "a_bit_of_everything")
    index.create_in(".", ABitOfEverythingSchema, "a_bit_of_everything")
    yield tmp_path


def test_analyser(indices: Path):
    schema = analyse(str(indices))
    assert schema.dialect == "whoosh"
    assert len(schema.indices) == 1


def test_generator(indices: Path, tmp_path: Path):
    schema = analyse(str(indices))

    models_dir = tmp_path / "models"
    os.mkdir(models_dir)

    generate(schema, models_dir, "models")
    os.makedirs("tmpmodels", exist_ok=True)
    generate(schema, Path("tmpmodels"), "models")

    sys.path.append(str(tmp_path))
    models = __import__("models")
