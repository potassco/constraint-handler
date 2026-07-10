from enum import IntEnum, auto


class Type(IntEnum):
    """
    Supported types.
    """
    NONE = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    SET = auto()
    FAIL = auto()
    DICT = auto()