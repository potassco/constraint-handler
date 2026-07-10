import typing
from flat_ch.core.types import Type
from flat_ch.core.operators import Operator
from flat_ch.operators.logic import handle_hasvalue, handle_if, handle_ite, handle_limp, handle_lnot
from flat_ch.operators.math import handle_add, handle_sub, handle_mult, handle_ceil, handle_floor, handle_minus, handle_sqrt, handle_float_div, handle_int_div, handle_max, handle_min
from flat_ch.operators.comparison import handle_eq, handle_neq, handle_leq, handle_lt, handle_gt, handle_geq

OperatorHandler = typing.Callable[
    [list[tuple[Type, typing.Any]]], 
    tuple[Type, typing.Any]
]

OPERATOR_HANDLERS: dict[Operator, OperatorHandler] = {
    Operator.HASVALUE: handle_hasvalue,
    Operator.IF: handle_if,
    Operator.ITE: handle_ite,
    Operator.LIMP: handle_limp,
    Operator.LNOT: handle_lnot,
    Operator.ADD: handle_add,
    Operator.SUB: handle_sub,
    Operator.MULT: handle_mult,
    Operator.FLOAT_DIV: handle_float_div,
    Operator.INT_DIV: handle_int_div,
    Operator.CEIL: handle_ceil,
    Operator.FLOOR: handle_floor,
    Operator.MINUS: handle_minus,
    Operator.SQRT: handle_sqrt,
    Operator.MAX: handle_max,
    Operator.MIN: handle_min,
    Operator.EQ:  handle_eq,
    Operator.NEQ: handle_neq,
    Operator.LEQ: handle_leq,
    Operator.LT:  handle_lt,
    Operator.GT:  handle_gt,
    Operator.GEQ: handle_geq,
}