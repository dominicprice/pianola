import inflect
import stringcase as sc

inflector = inflect.engine()


def unquote(s: str) -> str:
    quotechars = "\"'"
    for quotechar in quotechars:
        if s[0] == s[-1] == quotechar:
            return s[1:-1]
    raise ValueError("string is not quoted")


def quote(s: str, quotechar: str = '"') -> str:
    return quotechar + s + quotechar


def sql_to_module_name(s: str) -> str:
    if t := inflector.singular_noun(s):
        s = t
    return sc.lowercase(s)


def sql_to_class_name(s: str) -> str:
    if t := inflector.singular_noun(s):
        s = t
    return sc.pascalcase(s)


def sql_to_class_field(s: str) -> str:
    return sc.snakecase(s)
