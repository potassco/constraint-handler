from __future__ import annotations

import math

import constraint_handler.schemas.atom as atom
import constraint_handler.schemas.operators as operators
import constraint_handler.schemas.warning as warning
import constraint_handler.utils.common as common

NO_ERRORS: tuple[tuple[warning.Kind, str], ...] = ()


def evaluate_operator(o, args) -> atom.EvalResult:
    foldable = {operators.ArithmeticOperator.add: sum, operators.ArithmeticOperator.mult: math.prod}
    if o in foldable:
        return atom.EvalResult(foldable[o](args), NO_ERRORS)
    assert args
    if len(args) == 1:
        val = args[0]
        match o:
            case operators.ArithmeticOperator.sqrt:
                return atom.EvalResult(math.sqrt(val), NO_ERRORS)
            case operators.ArithmeticOperator.cos:
                return atom.EvalResult(math.cos(val), NO_ERRORS)
            case operators.ArithmeticOperator.sin:
                return atom.EvalResult(math.sin(val), NO_ERRORS)
            case operators.ArithmeticOperator.tan:
                return atom.EvalResult(math.tan(val), NO_ERRORS)
            case operators.ArithmeticOperator.abs:
                return atom.EvalResult(abs(val), NO_ERRORS)
            case operators.ArithmeticOperator.acos:
                return atom.EvalResult(math.acos(val), NO_ERRORS)
            case operators.ArithmeticOperator.asin:
                return atom.EvalResult(math.asin(val), NO_ERRORS)
            case operators.ArithmeticOperator.atan:
                return atom.EvalResult(math.atan(val), NO_ERRORS)
            case operators.ArithmeticOperator.minus:
                return atom.EvalResult(-val, NO_ERRORS)
            case operators.ArithmeticOperator.ceil:
                return atom.EvalResult(math.ceil(val), NO_ERRORS)
            case operators.ArithmeticOperator.floor:
                return atom.EvalResult(math.floor(val), NO_ERRORS)
            case operators.ArithmeticOperator.float_of_int:
                return atom.EvalResult(float(val), NO_ERRORS)
            case operators.ArithmeticOperator.int_of_float:
                return atom.EvalResult(int(val), NO_ERRORS)
    else:
        lval = args[0]
        rval = args[1]
        match o:
            case operators.ArithmeticOperator.sub:
                return atom.EvalResult(lval - rval, NO_ERRORS)
            case operators.ArithmeticOperator.int_div:
                if rval == 0:
                    return atom.EvalResult(
                        common.Bad.bad,
                        ((warning.Expression(warning.ExpressionWarning.zeroDivisionError), f"{lval}/{rval}"),),
                    )
                return atom.EvalResult(int(lval // rval), NO_ERRORS)
            case operators.ArithmeticOperator.float_div:
                if rval == 0:
                    return atom.EvalResult(
                        common.Bad.bad,
                        ((warning.Expression(warning.ExpressionWarning.zeroDivisionError), f"{lval}/{rval}"),),
                    )
                return atom.EvalResult(lval / rval, NO_ERRORS)
            case operators.ArithmeticOperator.pow:
                if rval == 0:
                    return atom.EvalResult(1, NO_ERRORS)
                if common.Bad.bad in args:
                    return atom.EvalResult(common.Bad.bad, NO_ERRORS)
                return atom.EvalResult(lval ** rval, NO_ERRORS)  # fmt: skip
            case operators.ArithmeticOperator.leq:
                return atom.EvalResult(lval <= rval, NO_ERRORS)
            case operators.ArithmeticOperator.lt:
                return atom.EvalResult(lval < rval, NO_ERRORS)
            case operators.ArithmeticOperator.geq:
                return atom.EvalResult(lval >= rval, NO_ERRORS)
            case operators.ArithmeticOperator.gt:
                return atom.EvalResult(lval > rval, NO_ERRORS)

    return atom.EvalResult(
        common.Bad.bad,
        ((warning.Expression(warning.ExpressionWarning.notImplemented), f"{o}"),),
    )
