import constraint_handler.schemas.warning as warning
import constraint_handler.utils.common as common
import constraint_handler.utils.errors as errors

Operator = common.PPEnum(
    "Operator", ["set_make", "set_isin", "set_notin", "union", "inter", "diff", "subset", "set_fold"]
)


def fold(f, s, start):
    # print("fold", f, s, start)
    accu = start
    for e in s:
        accu = f(e, accu)
    return accu


class Evaluator:
    def __init__(self, expr_evaluator, errors=None):
        self.expr_evaluator = expr_evaluator
        if errors is None:
            errors = []
        self.errors = errors

    def operator(self, o, args):
        match o:
            case Operator.set_make:
                if None in args:
                    return None
                return frozenset(args)
            case Operator.set_isin:
                if len(args) != 2:
                    self.errors.append(errors.incorrect_arity_error(o, 2, len(args)))
                    return None
                if args[1] is None:
                    return None
                return args[0] in args[1]
            case Operator.set_notin:
                if len(args) != 2:
                    self.errors.append(errors.incorrect_arity_error(o, 2, len(args)))
                    return None
                if args[1] is None:
                    return None
                return args[0] not in args[1]
            case Operator.union:
                if None in args:
                    return None
                return frozenset().union(*args)
            case Operator.inter:
                if len(args) < 1:
                    self.errors.append(errors.incorrect_arity_error(o, "at least 1", len(args)))
                    return None
                if None in args:
                    return None
                return frozenset(args[0].intersection(*args[1:]))
            case Operator.diff:
                if len(args) != 2:
                    self.errors.append(errors.incorrect_arity_error(o, 2, len(args)))
                    return None
                if None in args:
                    return None
                return frozenset(args[0].difference(args[1]))
            case Operator.subset:
                if len(args) != 2:
                    self.errors.append(errors.incorrect_arity_error(o, 2, len(args)))
                    return None
                if None in args:
                    return None
                return args[0].issubset(args[1])
            case Operator.set_fold:
                if len(args) != 3:
                    self.errors.append(errors.incorrect_arity_error(o, 3, len(args)))
                    return None
                if None in args:
                    return None
                evaluator = self.expr_evaluator()
                o = lambda *aaa: evaluator.operator(args[0], aaa)
                # TODO: log errors from evaluator
                return fold(o, args[1], args[2])
            case _:
                self.errors.append(
                    (warning.Expression(warning.ExpressionWarning.NotImplementedError), f"set.operator {o}")
                )
                return None
