from __future__ import annotations

import functools
import operator

import constraint_handler.schemas.atom as atom
import constraint_handler.schemas.operators as operators
import constraint_handler.schemas.warning as warning
import constraint_handler.utils.common as common

NO_ERRORS: tuple[tuple[warning.Kind, str], ...] = ()


def evaluate_operator(o, args) -> atom.EvalResult:
    match o:
        case operators.LogicOperator.conj:
            if False in args:
                return atom.EvalResult(False, NO_ERRORS)
            if common.Bad.bad in args:
                return atom.EvalResult(common.Bad.bad, NO_ERRORS)
            if None in args:
                return atom.EvalResult(None, NO_ERRORS)
            return atom.EvalResult(True, NO_ERRORS)
        case operators.LogicOperator.disj:
            if True in args:
                return atom.EvalResult(True, NO_ERRORS)
            if common.Bad.bad in args:
                return atom.EvalResult(common.Bad.bad, NO_ERRORS)
            if None in args:
                return atom.EvalResult(None, NO_ERRORS)
            return atom.EvalResult(False, NO_ERRORS)
        case operators.LogicOperator.ite:
            assert len(args) == 3
            if args[0] is None:
                return atom.EvalResult(None, NO_ERRORS)
            if args[0] is common.Bad.bad:
                return atom.EvalResult(common.Bad.bad, NO_ERRORS)
            return atom.EvalResult(args[1] if args[0] else args[2], NO_ERRORS)
        case operators.LogicOperator.leqv:
            if None in args:
                return atom.EvalResult(common.Bad.bad, NO_ERRORS)
            return atom.EvalResult(functools.reduce(operator.eq, args, True), NO_ERRORS)
        case operators.LogicOperator.limp:
            assert len(args) == 2
            if args[0] is False or args[1] is True:
                return atom.EvalResult(True, NO_ERRORS)
            if args[0] is True and args[1] is False:
                return atom.EvalResult(False, NO_ERRORS)
            if common.Bad.bad in args:
                return atom.EvalResult(common.Bad.bad, NO_ERRORS)
            if None in args:
                return atom.EvalResult(None, NO_ERRORS)
            return atom.EvalResult(
                common.Bad.bad, ((warning.Expression(warning.ExpressionWarning.evaluatorError), f"operation {o,args}"),)
            )
        case operators.LogicOperator.lnot:
            assert len(args) == 1
            if None in args:
                return atom.EvalResult(None, NO_ERRORS)
            return atom.EvalResult(not args[0], NO_ERRORS)
        case operators.LogicOperator.lxor:
            if None in args:
                return atom.EvalResult(common.Bad.bad, NO_ERRORS)
            return atom.EvalResult(functools.reduce(operator.xor, args, False), NO_ERRORS)
        case operators.LogicOperator.snot:
            assert len(args) == 1
            if None in args:
                return atom.EvalResult(False, NO_ERRORS)
            return atom.EvalResult(not args[0], NO_ERRORS)
        case operators.LogicOperator.wnot:
            assert len(args) == 1
            if None in args:
                return atom.EvalResult(True, NO_ERRORS)
            return atom.EvalResult(not args[0], NO_ERRORS)
        case _:
            return atom.EvalResult(
                common.Bad.bad,
                ((warning.Expression(warning.ExpressionWarning.notImplemented), f"logic_operator {o}"),),
            )
