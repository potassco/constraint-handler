"""Caller-facing, immutable expressions for declarative constraint input."""

from dataclasses import dataclass
from enum import StrEnum, auto

LABEL_ANONYMOUS = ""


class FailIntegrityExn(Exception):
    """Leave a Python-operation candidate undefined without rejecting its model."""


class Operator(StrEnum):
    """Enumerate the operators accepted by input expressions."""

    eq = auto()
    neq = auto()
    concat = auto()
    length = auto()
    max = auto()
    min = auto()
    get_or_else = auto()
    if_ = auto()
    has_value = auto()
    abs = auto()
    sqrt = auto()
    cos = auto()
    sin = auto()
    tan = auto()
    acos = auto()
    asin = auto()
    atan = auto()
    minus = auto()
    mod = auto()
    floor = auto()
    ceil = auto()
    add = auto()
    sub = auto()
    mult = auto()
    linear_integer = auto()
    linear_comparison = auto()
    int_div = auto()
    real_div = auto()
    pow = auto()
    leq = auto()
    lt = auto()
    geq = auto()
    gt = auto()
    real_from_int = auto()
    int_from_real = auto()
    conj = auto()
    disj = auto()
    ite = auto()
    leqv = auto()
    limp = auto()
    lnot = auto()
    lxor = auto()
    snot = auto()
    wnot = auto()
    cardinality = auto()
    set_make = auto()
    set_isin = auto()
    set_notin = auto()
    union = auto()
    inter = auto()
    diff = auto()
    subset = auto()
    set_fold = auto()
    make_tuple = auto()
    tuple_get = auto()
    python_eval = auto()
    lambda_ = auto()


@dataclass(frozen=True, slots=True)
class VariableRef:
    """Refer to a variable by name without resolving its value."""

    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True, slots=True)
class Operation:
    """Describe an operator applied to unevaluated argument expressions."""

    op: Operator
    args: tuple[OperationArg, ...]


@dataclass(frozen=True, slots=True)
class Lambda:
    """Bind named parameters to an unevaluated expression body."""

    vars: tuple[VariableRef, ...]
    expr: Expr


@dataclass(frozen=True, slots=True)
class Python:
    """Retain Python expression source for later evaluation."""

    fn: str

    def __str__(self) -> str:
        return self.fn


type Value = bool | float | int | str | None
type Set = frozenset[Expr]
type Tuple = tuple[Expr, ...]
type Expr = VariableRef | Value | Set | Tuple | Operation
type OperationArg = Expr | Lambda | Python
