import os
import sys
import tempfile
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Generator

import pysqlite3
import pytest
from pianola.analyse.sqlite import analyse
from pianola.generate.sqlite import generate

FILE = Path(os.path.dirname(os.path.realpath(__file__)))


@pytest.fixture
def db() -> Generator[str, None, None]:
    dbfile = tempfile.mktemp()

    with open(FILE / "schemas" / "abitofeverything.sql") as f:
        with pysqlite3.connect(dbfile) as conn:
            conn.executescript(f.read())

    yield dbfile

    os.unlink(dbfile)


def test_analyser(db: str):
    schema = analyse(db)
    assert schema.dialect == "sqlite"
    assert len(schema.tables) == 13

    table = schema.find_table("a_bit_of_everything", False)
    assert len(table.columns) == 46
    assert len(table.indices) == 0

    col1 = table.find_column("a_boolean_nullable", False)
    assert col1.sqltype == "BOOLEAN"
    assert col1.nullable == True
    assert col1.pytype == "Optional[bool]"


def test_generator(db: str, tmp_path: Path):
    schema = analyse(db)

    models_dir = tmp_path / "models"
    os.mkdir(models_dir)

    generate(schema, models_dir, "models")
    sys.path.append(str(tmp_path))
    models = __import__("models")

    with pysqlite3.connect(db) as conn:
        cursor = conn.cursor()
        r1 = models.ABitOfEverything(
            1,
            None,
            b"",
            None,
            True,
            None,
            False,
            None,
            "a",
            None,
            b"",
            None,
            date.today(),
            None,
            datetime.now(),
            None,
            Decimal(1.25),
            None,
            1.23,
            None,
            2.34,
            None,
            5,
            None,
            7,
            None,
            "abc",
            None,
            9.12,
            None,
            "bcd",
            None,
            3.56,
            None,
            1,
            None,
            "hello",
            None,
            time(1, 2, 3),
            None,
            datetime.now(),
            None,
            2,
            None,
            "bye",
            None,
        )
    r1.insert(cursor)

    res = list(models.ABitOfEverything.get(cursor))
    assert len(res) == 1

    s1 = res[0]
    assert r1.a_bigint == s1.a_bigint
    assert r1.a_bigint_nullable == s1.a_bigint_nullable
    assert r1.a_blob == s1.a_blob
    assert r1.a_blob_nullable == s1.a_blob_nullable
    assert r1.a_bool == s1.a_bool
    assert r1.a_bool_nullable == s1.a_bool_nullable
    assert r1.a_boolean == s1.a_boolean
    assert r1.a_boolean_nullable == s1.a_boolean_nullable
    assert r1.a_character == s1.a_character
    assert r1.a_character_nullable == s1.a_character_nullable
    assert r1.a_clob == s1.a_clob
    assert r1.a_clob_nullable == s1.a_clob_nullable
    assert r1.a_date == s1.a_date
    assert r1.a_date_nullable == s1.a_date_nullable
    assert r1.a_datetime == s1.a_datetime
    assert r1.a_datetime_nullable == s1.a_datetime_nullable
    assert r1.a_decimal == s1.a_decimal
    assert r1.a_decimal_nullable == s1.a_decimal_nullable
    assert r1.a_double == s1.a_double
    assert r1.a_double_nullable == s1.a_double_nullable
    assert r1.a_float == s1.a_float
    assert r1.a_float_nullable == s1.a_float_nullable
    assert r1.a_int == s1.a_int
    assert r1.a_int_nullable == s1.a_int_nullable
    assert r1.a_integer == s1.a_integer
    assert r1.a_integer_nullable == s1.a_integer_nullable
    assert r1.a_nchar == s1.a_nchar
    assert r1.a_nchar_nullable == s1.a_nchar_nullable
    assert r1.a_numeric == s1.a_numeric
    assert r1.a_numeric_nullable == s1.a_numeric_nullable
    assert r1.a_nvarchar == s1.a_nvarchar
    assert r1.a_nvarchar_nullable == s1.a_nvarchar_nullable
    assert r1.a_real == s1.a_real
    assert r1.a_real_nullable == s1.a_real_nullable
    assert r1.a_smallint == s1.a_smallint
    assert r1.a_smallint_nullable == s1.a_smallint_nullable
    assert r1.a_text == s1.a_text
    assert r1.a_text_nullable == s1.a_text_nullable
    assert r1.a_time == s1.a_time
    assert r1.a_time_nullable == s1.a_time_nullable
    assert r1.a_timestamp == s1.a_timestamp
    assert r1.a_timestamp_nullable == s1.a_timestamp_nullable
    assert r1.a_tinyint == s1.a_tinyint
    assert r1.a_tinyint_nullable == s1.a_tinyint_nullable
    assert r1.a_varchar == s1.a_varchar
    assert r1.a_varchar_nullable == s1.a_varchar_nullable

    r2 = models.APrimary()
    r2.insert(cursor)
    assert r2.a_key != 0

    r3 = models.AForeignKey(a_key=r2.a_key)
    r3.insert(cursor)

    r4 = models.APrimaryComposite(1, 2)
    r4.insert(cursor)
    assert r4.a_key1 == 1
    assert r4.a_key2 == 2
