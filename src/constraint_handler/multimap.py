from collections.abc import Callable

import constraint_handler.set as myset
from constraint_handler.utils.common import PPEnum

Operator = PPEnum(
    "Operator",
    [
        "find",
        "find2",
        "isin",
        "multimap_make",
        "multimap_fold",
        "multimap_fold_i",
        "countKeys",
        "countEntries",
        "sumIntEntries",
        "maxEntries",
        "minEntries",
    ],
)


class HashableDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))

    def __repr__(self):
        kv = ", ".join(f"{str(k)}:{str(v)}" for k, v in self.items())
        return f"{{{kv}}}"


def fold(f, m, start):
    accu = start
    for key in m:
        value = m[key]
        accu = myset.fold(f, value, accu)
    return accu


def fold_i(f, m, start):
    accu = start
    for key in m:
        value = m[key]
        for val in value:
            accu = f(key, val, accu)
    return accu


def compare(multimap: HashableDict, op: Callable):
    best_val = None
    errors: list[Exception] = []
    try:
        for key, value in multimap.items():
            local_best = op(value)
            if best_val is None:
                best_val = local_best
            elif local_best is not None:
                best_val = op(best_val, local_best)
    except TypeError as exn:
        errors.append(NotImplementedError(f"multimap does not support comparison of values of some types: {exn}"))
    except Exception as exn:
        errors.append(exn)
    return best_val, errors


class Evaluator:
    def __init__(self, errors=None):
        if errors is None:
            errors = []
        self.errors = errors

    def operator(self, o, args):
        if None in args:
            return None
        match o:
            case Operator.isin:
                assert len(args) == 2
                return args[0] in args[1]
            case Operator.find:
                assert len(args) == 2
                return args[1][args[0]] if args[0] in args[1] else frozenset()
            case Operator.find2:
                # args is dict, key, value
                # return if value in d[key]
                assert len(args) == 3
                return args[1] in args[0] and args[2] in args[0][args[1]]
            case Operator.multimap_fold:
                o = lambda *aaa: self.operator(args[0], aaa)  # TODO: check
                return fold(o, args[1], args[2])
            case Operator.multimap_fold_i:
                o = lambda *aaa: self.operator(args[0], aaa)  # TODO: check
                return fold_i(o, args[1], args[2])
            case Operator.multimap_make:
                d = HashableDict()
                for key, value in args:
                    if key not in d:
                        d[key] = {value}
                    else:
                        d[key].add(value)
                for key, value in d.items():
                    d[key] = frozenset(value)
                return d

            case Operator.countKeys:
                return len(args[0])

            case Operator.countEntries:
                count = 0
                for key, value in args[0].items():
                    count += len(value)
                return count

            case Operator.sumIntEntries:
                total = 0
                for key, value in args[0].items():
                    total += sum(v for v in value if isinstance(v, int))
                return total

            case Operator.maxEntries:
                __max, erros = compare(args[0], max)
                self.errors.extend(erros)
                return __max
            case Operator.minEntries:
                __min, erros = compare(args[0], min)
                self.errors.extend(erros)
                return __min
            case _:
                self.errors.append(NotImplementedError(f"multimap.operator {o}"))
                return None
