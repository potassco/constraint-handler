from __future__ import annotations

import math

import constraint_handler.schemas.warning as warning
import constraint_handler.utils.common as common

Operator = common.PPEnum(
    "Operator",
    [
        "abs",
        "sqrt",
        "cos",
        "sin",
        "tan",
        "acos",
        "asin",
        "atan",
        "minus",
        "floor",
        "ceil",
        "add",
        "sub",
        "mult",
        "int_div",
        "fdiv",
        "pow",
        "leq",
        "lt",
        "geq",
        "gt",
    ],
)


class Evaluator:
    def __init__(self, expr_evaluator, errors=None):
        self.expr_evaluator = expr_evaluator
        if errors is None:
            errors = []
        self.errors = errors

    def operator(self, o, args):
        if common.Bad.bad in args:
            return common.Bad.bad
        if None in args:
            return None
        foldable = {Operator.add: sum, Operator.mult: math.prod}
        if o in foldable:
            return foldable[o](args)
        assert args
        if len(args) == 1:
            val = args[0]
            match o:
                case Operator.sqrt:
                    return math.sqrt(val)
                case Operator.cos:
                    return math.cos(val)
                case Operator.sin:
                    return math.sin(val)
                case Operator.tan:
                    return math.tan(val)
                case Operator.abs:
                    return abs(val)
                case Operator.acos:
                    return math.acos(val)
                case Operator.asin:
                    return math.asin(val)
                case Operator.atan:
                    return math.atan(val)
                case Operator.minus:
                    return -val
                case Operator.ceil:
                    return math.ceil(val)
                case Operator.floor:
                    return math.floor(val)
        else:
            lval = args[0]
            rval = args[1]
            match o:
                case Operator.sub:
                    return lval - rval
                case Operator.int_div:
                    if rval == 0:
                        self.errors.append(
                            (warning.Expression(warning.ExpressionWarning.zeroDivisionError), f"{lval}/{rval}")
                        )
                        return common.Bad.bad
                    return int(lval // rval)
                case Operator.fdiv:
                    if rval == 0:
                        self.errors.append(
                            (warning.Expression(warning.ExpressionWarning.zeroDivisionError), f"{lval}/{rval}")
                        )
                        return common.Bad.bad
                    return lval / rval
                case Operator.pow:
                    return lval ** rval  # fmt: skip
                case Operator.leq:
                    return lval <= rval
                case Operator.lt:
                    return lval < rval
                case Operator.geq:
                    return lval >= rval
                case Operator.gt:
                    return lval > rval
                case _:
                    self.errors.append((warning.Expression(warning.ExpressionWarning.notImplemented), f"unop {o}"))
                    return common.Bad.bad
