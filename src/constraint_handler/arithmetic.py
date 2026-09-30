from __future__ import annotations

import math

import constraint_handler.schemas.operators as operators
import constraint_handler.schemas.result as result
import constraint_handler.schemas.warning as warning
import constraint_handler.utils.common as common

NO_ERRORS: tuple[tuple[warning.Kind, str], ...] = ()


def evaluate_operator(o, args) -> result.EvalResult:
    foldable = {operators.ArithmeticOperator.add: sum, operators.ArithmeticOperator.mult: math.prod}
    if o in foldable:
        return result.EvalResult(foldable[o](args), NO_ERRORS)
    assert args
    if len(args) == 1:
        val = args[0]
        match o:
            case operators.ArithmeticOperator.sqrt:
                return result.EvalResult(math.sqrt(val), NO_ERRORS)
            case operators.ArithmeticOperator.cos:
                return result.EvalResult(math.cos(val), NO_ERRORS)
            case operators.ArithmeticOperator.sin:
                return result.EvalResult(math.sin(val), NO_ERRORS)
            case operators.ArithmeticOperator.tan:
                return result.EvalResult(math.tan(val), NO_ERRORS)
            case operators.ArithmeticOperator.abs:
                return result.EvalResult(abs(val), NO_ERRORS)
            case operators.ArithmeticOperator.acos:
                return result.EvalResult(math.acos(val), NO_ERRORS)
            case operators.ArithmeticOperator.asin:
                return result.EvalResult(math.asin(val), NO_ERRORS)
            case operators.ArithmeticOperator.atan:
                return result.EvalResult(math.atan(val), NO_ERRORS)
            case operators.ArithmeticOperator.minus:
                return result.EvalResult(-val, NO_ERRORS)
            case operators.ArithmeticOperator.ceil:
                return result.EvalResult(math.ceil(val), NO_ERRORS)
            case operators.ArithmeticOperator.floor:
                return result.EvalResult(math.floor(val), NO_ERRORS)
            case operators.ArithmeticOperator.float_from_int:
                return result.EvalResult(float(val), NO_ERRORS)
            case operators.ArithmeticOperator.int_from_float:
                return result.EvalResult(int(val), NO_ERRORS)
    else:
        lval = args[0]
        rval = args[1]
        match o:
            case operators.ArithmeticOperator.sub:
                return result.EvalResult(lval - rval, NO_ERRORS)
            case operators.ArithmeticOperator.int_div:
                if rval == 0:
                    return result.EvalResult(
                        common.Bad.bad,
                        ((warning.Expression(warning.ExpressionWarning.zeroDivisionError), f"{lval}/{rval}"),),
                    )
                return result.EvalResult(int(lval // rval), NO_ERRORS)
            case operators.ArithmeticOperator.float_div:
                if rval == 0:
                    return result.EvalResult(
                        common.Bad.bad,
                        ((warning.Expression(warning.ExpressionWarning.zeroDivisionError), f"{lval}/{rval}"),),
                    )
                return result.EvalResult(lval / rval, NO_ERRORS)
            case operators.ArithmeticOperator.mod:
                if rval == 0:
                    return result.EvalResult(
                        common.Bad.bad,
                        ((warning.Expression(warning.ExpressionWarning.zeroDivisionError), f"{lval}%{rval}"),),
                    )
                return result.EvalResult(lval % rval, NO_ERRORS)
            case operators.ArithmeticOperator.pow:
                if rval == 0:
                    return result.EvalResult(1, NO_ERRORS)
                if common.Bad.bad in args:
                    return result.EvalResult(common.Bad.bad, NO_ERRORS)
                return result.EvalResult(lval ** rval, NO_ERRORS)  # fmt: skip
            case operators.ArithmeticOperator.leq:
                return result.EvalResult(lval <= rval, NO_ERRORS)
            case operators.ArithmeticOperator.lt:
                return result.EvalResult(lval < rval, NO_ERRORS)
            case operators.ArithmeticOperator.geq:
                return result.EvalResult(lval >= rval, NO_ERRORS)
            case operators.ArithmeticOperator.gt:
                return result.EvalResult(lval > rval, NO_ERRORS)

    return result.EvalResult(
        common.Bad.bad,
        ((warning.Expression(warning.ExpressionWarning.notImplemented), f"{o}"),),
    )
