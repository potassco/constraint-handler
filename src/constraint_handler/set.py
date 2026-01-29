import constraint_handler.evaluator as full_evaluator
from constraint_handler.utils.common import PPEnum
from constraint_handler.utils import testing

Operator = PPEnum("Operator", ["makeSet", "isin", "notin", "union", "inter", "diff", "subset", "set_fold"])


def fold(f, s, start):
    # print("fold", f, s, start)
    accu = start
    for e in s:
        accu = f(e, accu)
    return accu


class Evaluator:
    def __init__(self, errors=None):
        if errors is None:
            errors = []
        self.errors = errors

    def operator(self, o, args):
        if None in args:
            return None
        match o:
            case Operator.makeSet:
                return frozenset(args)
            case Operator.isin:
                if len(args) != 2:
                    self.errors.append(testing.incorrect_arity_error(Operator.isin, 2, len(args)))
                    return None
                return args[0] in args[1]
            case Operator.notin:
                if len(args) != 2:
                    self.errors.append(testing.incorrect_arity_error(Operator.notin, 2, len(args)))
                    return None
                return args[0] not in args[1]
            case Operator.union:
                return frozenset().union(*args)
            case Operator.inter:
                if len(args) < 1:
                    self.errors.append(testing.incorrect_arity_error(Operator.inter, "at least 1", len(args)))
                    return None
                return frozenset(args[0].intersection(*args[1:]))
            case Operator.diff:
                if len(args) != 2:
                    self.errors.append(testing.incorrect_arity_error(Operator.diff, 2, len(args)))
                    return None
                return frozenset(args[0].difference(args[1]))
            case Operator.subset:
                if len(args) != 2:
                    self.errors.append(testing.incorrect_arity_error(Operator.subset, 2, len(args)))
                    return None
                return args[0].issubset(args[1])
            case Operator.set_fold:
                if len(args) != 3:
                    self.errors.append(testing.incorrect_arity_error(Operator.set_fold, 3, len(args)))
                    return None
                evaluator = full_evaluator.Evaluator()
                o = lambda *aaa: evaluator.operator(args[0], aaa)
                return fold(o, args[1], args[2])
            case _:
                self.errors.append(NotImplementedError(f"set.operator {o}"))
                return None
