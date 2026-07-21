from enum import IntEnum, IntFlag, auto


class Arity(IntFlag):
    """Bitflags representing the structural arities an operator supports."""

    UNARY = 1 << 1
    BINARY = 1 << 2
    TERNARY = 1 << 3
    VARIADIC = 1 << 4


class Operator(IntEnum):
    CONJ = auto()
    DISJ = auto()
    HASVALUE = auto()
    IF = auto()
    ITE = auto()
    LIMP = auto()
    LNOT = auto()
    ADD = auto()
    FLOAT_ADD = auto()
    SUB = auto()
    MULT = auto()
    FLOAT_DIV = auto()
    INT_DIV = auto()
    CEIL = auto()
    FLOOR = auto()
    MINUS = auto()
    SQRT = auto()
    MAX = auto()
    MIN = auto()
    EQ = auto()
    NEQ = auto()
    LEQ = auto()
    LT = auto()
    GT = auto()
    GEQ = auto()
    SET_MAKE = auto()
    SET_ISIN = auto()
    UNION = auto()
    DIFF = auto()
    INTER = auto()
    SUBSET = auto()
    LENGTH = auto()
    SET_NOTIN = auto()
    PYTHON = auto()
    DICT_MAKE = auto()
    DICT_SELECT = auto()
    LEQV = auto()
    LXOR = auto()
    SNOT = auto()
    WNOT = auto()
    ABS = auto()
    POW = auto()
    CONCAT = auto()

    @property
    def allowed_arities(self) -> Arity:
        """Returns the bitmask of all structural shapes this operator permits."""
        return _OPERATOR_ARITY_MASKS.get(self, Arity.BINARY)

    @property
    def asp_name(self) -> str:
        """Returns the exact string identifier used in ASP schema predicates."""
        if self == Operator.HASVALUE:
            return "hasValue"
        return self.name.lower()


# Map variations seamlessly using bitwise OR combinators
_OPERATOR_ARITY_MASKS = {
    # Unary Only
    Operator.HASVALUE: Arity.UNARY,
    Operator.SNOT: Arity.UNARY,
    Operator.WNOT: Arity.UNARY,
    Operator.LNOT: Arity.UNARY,
    Operator.ABS: Arity.UNARY,
    Operator.MINUS: Arity.UNARY,
    Operator.LENGTH: Arity.UNARY,
    Operator.CEIL: Arity.UNARY,
    Operator.FLOOR: Arity.UNARY,
    Operator.SQRT: Arity.UNARY,
    # Binary Only
    Operator.POW: Arity.BINARY,
    Operator.CONCAT: Arity.BINARY,
    # Ternary Only
    Operator.ITE: Arity.TERNARY,
    # Inherently Variadic Collections
    Operator.SET_MAKE: Arity.VARIADIC,
    Operator.DICT_MAKE: Arity.VARIADIC,
    Operator.PYTHON: Arity.VARIADIC,
    # Flexible Operators (Supports BOTH pure binary and dynamic variadic shapes!)
    Operator.ADD: Arity.BINARY | Arity.VARIADIC,
    Operator.MULT: Arity.BINARY | Arity.VARIADIC,
    Operator.CONJ: Arity.VARIADIC,
    Operator.DISJ: Arity.VARIADIC,
    Operator.LEQV: Arity.BINARY | Arity.VARIADIC,
    Operator.LXOR: Arity.BINARY | Arity.VARIADIC,
}
