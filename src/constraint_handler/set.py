import constraint_handler.evaluator as full_evaluator
from constraint_handler.utils.common import PPEnum

Operator = PPEnum("Operator", ["makeSet", "isin", "notin", "union", "inter", "subset", "set_fold"])


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
                return args[0] in args[1]
            case Operator.notin:
                return args[0] not in args[1]
            case Operator.union:
                return frozenset().union(*args)
            case Operator.inter:
                return frozenset(args[0].intersection(*args[1:]))
            case Operator.subset:
                return args[0].issubset(args[1])
            case Operator.set_fold:
                evaluator = full_evaluator.Evaluator()
                o = lambda *aaa: evaluator.operator(args[0], aaa)
                return fold(o, args[1], args[2])
            case _:
                self.errors.append(NotImplementedError(f"set.operator {o}"))
                return None
