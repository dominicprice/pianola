from typing import Optional

from pianola.lib.schema.sql.column import Column

BOOLEAN_TYPES = ["BOOLEAN"]

INTEGER_TYPES = ["INT", "INTEGER", "TINYINT", "SMALLINT", "MEDIUMINT", "BIGINT"]

STRING_TYPES = ["CHAR", "CHARACTER", "NCHAR", "NVARCHAR", "VARCHAR", "TEXT"]

BYTES_TYPES = ["BLOB", "VARBINARY"]

FLOAT_TYPES = ["REAL", "DOUBLE", "FLOAT"]

NUMERIC_TYPES = ["NUMERIC"]

DECIMAL_TYPES = ["DECIMAL"]

DATE_TYPES = ["DATE"]

TIME_TYPES = ["TIME"]

DATETIME_TYPES = ["DATETIME", "TIMESTAMP"]


def col_add_pytype(column: Column):
    sqltype = column.sqltype
    pytype = ""
    conv_func: Optional[str] = None
    if sqltype.upper() in INTEGER_TYPES:
        pytype = "int"
    elif sqltype.upper() in STRING_TYPES:
        pytype = "str"
    elif sqltype.upper() in BYTES_TYPES:
        pytype = "bytes"
    elif sqltype.upper() in FLOAT_TYPES:
        pytype = "float"
    elif sqltype.upper() in NUMERIC_TYPES:
        pytype = "Union[int, float]"
    elif sqltype.upper() in BOOLEAN_TYPES:
        pytype = "bool"
    elif sqltype.upper() in DATE_TYPES:
        pytype = "date"
        conv_func = "date"
    elif sqltype.upper() in DECIMAL_TYPES:
        pytype = "Decimal"
        conv_func = "decimal"
    elif sqltype.upper() in TIME_TYPES:
        pytype = "time"
        conv_func = "time"
    elif sqltype.upper() in DATETIME_TYPES:
        pytype = "datetime"
        conv_func = "datetime"
    else:
        raise ValueError("unable to cast sql type '" + sqltype + "' into a python type")

    if column.nullable:
        pytype = "Optional[" + pytype + "]"
    column.pytype = pytype
    column.conv_func = conv_func
