from __future__ import annotations

import functools
import operator

import constraint_handler.schemas.operators as operators
import constraint_handler.schemas.result as result
import constraint_handler.schemas.warning as warning
import constraint_handler.utils.common as common

NO_ERRORS: tuple[tuple[warning.Kind, str], ...] = ()


def evaluate_operator(o, args) -> result.EvalResult:
    match o:
        case operators.LogicOperator.conj:
            if False in args:
                return result.EvalResult(False, NO_ERRORS)
            if common.Bad.bad in args:
                return result.EvalResult(common.Bad.bad, NO_ERRORS)
            if None in args:
                return result.EvalResult(None, NO_ERRORS)
            return result.EvalResult(True, NO_ERRORS)
        case operators.LogicOperator.disj:
            if True in args:
                return result.EvalResult(True, NO_ERRORS)
            if common.Bad.bad in args:
                return result.EvalResult(common.Bad.bad, NO_ERRORS)
            if None in args:
                return result.EvalResult(None, NO_ERRORS)
            return result.EvalResult(False, NO_ERRORS)
        case operators.LogicOperator.leqv:
            if None in args:
                return result.EvalResult(common.Bad.bad, NO_ERRORS)
            return result.EvalResult(functools.reduce(operator.eq, args, True), NO_ERRORS)
        case operators.LogicOperator.limp:
            assert len(args) == 2
            if args[0] is False or args[1] is True:
                return result.EvalResult(True, NO_ERRORS)
            if args[0] is True and args[1] is False:
                return result.EvalResult(False, NO_ERRORS)
            if common.Bad.bad in args:
                return result.EvalResult(common.Bad.bad, NO_ERRORS)
            if None in args:
                return result.EvalResult(None, NO_ERRORS)
            return result.EvalResult(
                common.Bad.bad, ((warning.Expression(warning.ExpressionWarning.evaluatorError), f"operation {o,args}"),)
            )
        case operators.LogicOperator.lnot:
            assert len(args) == 1
            if None in args:
                return result.EvalResult(None, NO_ERRORS)
            return result.EvalResult(not args[0], NO_ERRORS)
        case operators.LogicOperator.lxor:
            if None in args:
                return result.EvalResult(common.Bad.bad, NO_ERRORS)
            return result.EvalResult(functools.reduce(operator.xor, args, False), NO_ERRORS)
        case operators.LogicOperator.snot:
            assert len(args) == 1
            if None in args:
                return result.EvalResult(False, NO_ERRORS)
            return result.EvalResult(not args[0], NO_ERRORS)
        case operators.LogicOperator.wnot:
            assert len(args) == 1
            if None in args:
                return result.EvalResult(True, NO_ERRORS)
            return result.EvalResult(not args[0], NO_ERRORS)
        case _:
            return result.EvalResult(
                common.Bad.bad,
                ((warning.Expression(warning.ExpressionWarning.notImplemented), f"logic_operator {o}"),),
            )
