from pathlib import Path

from pianola.lib.writer import Writer


def generate_converters(outdir: Path):
    with Writer(outdir / "converters.py") as w:
        w.writeline("from typing import Optional")
        w.writeline("from datetime import date, datetime, time")
        w.writeline("from decimal import Decimal")
        w.writeline()

        w.writeline("def datetime_to_sql(dt: datetime) -> str:")
        with w.indented():
            w.writeline("return dt.isoformat()")
        w.writeline()

        w.writeline("def datetime_from_sql(dt: str) -> datetime:")
        with w.indented():
            w.writeline("return datetime.fromisoformat(dt)")
        w.writeline()

        w.writeline(
            "def optional_datetime_to_sql(dt: Optional[datetime]) -> Optional[str]:"
        )
        with w.indented():
            w.writeline("if dt is None:")
            with w.indented():
                w.writeline("return None")
            w.writeline("return datetime_to_sql(dt)")
        w.writeline()

        w.writeline(
            "def optional_datetime_from_sql(dt: Optional[str]) -> Optional[datetime]:"
        )
        with w.indented():
            w.writeline("if dt is None:")
            with w.indented():
                w.writeline("return None")
            w.writeline("return datetime_from_sql(dt)")
        w.writeline()

        w.writeline("def date_to_sql(dt: date) -> str:")
        with w.indented():
            w.writeline("return dt.isoformat()")
        w.writeline()

        w.writeline("def date_from_sql(dt: str) -> date:")
        with w.indented():
            w.writeline("return date.fromisoformat(dt)")
        w.writeline()

        w.writeline("def optional_date_to_sql(dt: Optional[date]) -> Optional[str]:")
        with w.indented():
            w.writeline("if dt is None:")
            with w.indented():
                w.writeline("return None")
            w.writeline("return date_to_sql(dt)")
        w.writeline()

        w.writeline("def optional_date_from_sql(dt: Optional[str]) -> Optional[date]:")
        with w.indented():
            w.writeline("if dt is None:")
            with w.indented():
                w.writeline("return None")
            w.writeline("return date_from_sql(dt)")
        w.writeline()

        w.writeline("def time_to_sql(dt: time) -> str:")
        with w.indented():
            w.writeline("return dt.isoformat()")
        w.writeline()

        w.writeline("def time_from_sql(dt: str) -> time:")
        with w.indented():
            w.writeline("return time.fromisoformat(dt)")
        w.writeline()

        w.writeline("def optional_time_to_sql(dt: Optional[time]) -> Optional[str]:")
        with w.indented():
            w.writeline("if dt is None:")
            with w.indented():
                w.writeline("return None")
            w.writeline("return time_to_sql(dt)")
        w.writeline()

        w.writeline("def optional_time_from_sql(dt: Optional[str]) -> Optional[time]:")
        with w.indented():
            w.writeline("if dt is None:")
            with w.indented():
                w.writeline("return None")
            w.writeline("return time_from_sql(dt)")
        w.writeline()

        w.writeline("def decimal_to_sql(d: Decimal) -> float:")
        with w.indented():
            w.writeline("return float(d)")
        w.writeline()

        w.writeline("def decimal_from_sql(d: float) -> Decimal:")
        with w.indented():
            w.writeline("return Decimal(d)")
        w.writeline()

        w.writeline(
            "def optional_decimal_to_sql(d: Optional[Decimal]) -> Optional[float]:"
        )
        with w.indented():
            w.writeline("if d is None:")
            with w.indented():
                w.writeline("return None")
            w.writeline("return decimal_to_sql(d)")
        w.writeline()

        w.writeline(
            "def optional_decimal_from_sql(d: Optional[float]) -> Optional[Decimal]:"
        )
        with w.indented():
            w.writeline("if d is None:")
            with w.indented():
                w.writeline("return None")
            w.writeline("return decimal_from_sql(d)")
