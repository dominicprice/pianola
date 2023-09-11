from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class Column:
    sqlname: str = ""
    pyname: str = ""
    quoted: bool = False
    sqltype: str = ""
    pytype: str = ""
    conv_func: Optional[str] = None
    nullable: bool = True
    default_value: Union[str, int, float, None] = None
    primary_key: bool = False
    reference: Optional["Column"] = None

    def val_from_sql(self, s: str) -> str:
        if self.conv_func is None:
            return s
        return (
            ("optional_" if self.nullable else "")
            + self.conv_func
            + "_from_sql("
            + s
            + ")"
        )

    def val_to_sql(self, s: str) -> str:
        if self.conv_func is None:
            return s
        return (
            ("optional_" if self.nullable else "")
            + self.conv_func
            + "_to_sql("
            + s
            + ")"
        )
