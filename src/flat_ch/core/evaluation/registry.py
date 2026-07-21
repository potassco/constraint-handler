import typing

from flat_ch.core.evaluation.comparison import handle_eq, handle_geq, handle_gt, handle_leq, handle_lt, handle_neq
from flat_ch.core.evaluation.logic import (
    handle_hasvalue,
    handle_if,
    handle_ite,
    handle_leqv,
    handle_limp,
    handle_lnot,
    handle_lxor,
    handle_snot,
    handle_wnot,
)
from flat_ch.core.evaluation.math import (
    handle_abs,
    handle_add,
    handle_ceil,
    handle_concat,
    handle_float_div,
    handle_floor,
    handle_int_div,
    handle_length,
    handle_max,
    handle_min,
    handle_minus,
    handle_mult,
    handle_pow,
    handle_sqrt,
    handle_sub,
)
from flat_ch.core.evaluation.operators import Operator
from flat_ch.core.types import Type

OperatorHandler = typing.Callable[[list[tuple[Type, typing.Any]]], tuple[Type, typing.Any]]

OPERATOR_HANDLERS: dict[Operator, OperatorHandler] = {
    Operator.HASVALUE: handle_hasvalue,
    Operator.IF: handle_if,
    Operator.ITE: handle_ite,
    Operator.LIMP: handle_limp,
    Operator.LEQV: handle_leqv,
    Operator.LNOT: handle_lnot,
    Operator.LXOR: handle_lxor,
    Operator.SNOT: handle_snot,
    Operator.WNOT: handle_wnot,
    Operator.ABS: handle_abs,
    Operator.ADD: handle_add,
    Operator.SUB: handle_sub,
    Operator.MULT: handle_mult,
    Operator.FLOAT_DIV: handle_float_div,
    Operator.INT_DIV: handle_int_div,
    Operator.POW: handle_pow,
    Operator.CEIL: handle_ceil,
    Operator.FLOOR: handle_floor,
    Operator.LENGTH: handle_length,
    Operator.CONCAT: handle_concat,
    Operator.MINUS: handle_minus,
    Operator.SQRT: handle_sqrt,
    Operator.MAX: handle_max,
    Operator.MIN: handle_min,
    Operator.EQ: handle_eq,
    Operator.NEQ: handle_neq,
    Operator.LEQ: handle_leq,
    Operator.LT: handle_lt,
    Operator.GT: handle_gt,
    Operator.GEQ: handle_geq,
}
