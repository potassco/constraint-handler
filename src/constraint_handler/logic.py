from __future__ import annotations

import functools
import operator

import constraint_handler.schemas.warning as warning
import constraint_handler.utils.common as common

Operator = common.PPEnum("Operator", ["conj", "disj", "ite", "leqv", "limp", "lnot", "lxor", "snot", "wnot"])


class Evaluator:
    def __init__(self, expr_evaluator, errors=None):
        self.expr_evaluator = expr_evaluator
        if errors is None:
            errors = []
        self.errors = errors

    def operator(self, o, args):
        match o:
            case Operator.conj:
                if False in args:
                    return False
                elif None in args:
                    return None
                else:
                    return True
            case Operator.disj:
                if True in args:
                    return True
                elif None in args:
                    return None
                else:
                    return False
            case Operator.ite:
                assert len(args) == 3
                if args[0] is None:
                    return None
                return args[1] if args[0] else args[2]
            case Operator.leqv:
                if None in args:
                    return None
                return functools.reduce(operator.eq, args, True)
            case Operator.limp:
                assert len(args) == 2
                return args[1] if args[0] else True
            case Operator.lnot:
                assert len(args) == 1
                if None in args:
                    return None
                return not args[0]
            case Operator.lxor:
                if None in args:
                    return None
                return functools.reduce(operator.xor, args, False)
            case Operator.snot:
                assert len(args) == 1
                if None in args:
                    return False
                return not args[0]
            case Operator.wnot:
                assert len(args) == 1
                if None in args:
                    return True
                return not args[0]
            case _:
                self.errors.append(
                    (warning.Expression(warning.ExpressionWarning.notImplemented), f"logic_operator {o}")
                )
                return common.Bad.bad
