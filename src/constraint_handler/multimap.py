import typing
from collections.abc import Callable, Iterator, Mapping

import constraint_handler.schemas.atom as atom
import constraint_handler.schemas.operators as operators
import constraint_handler.schemas.warning as warning
import constraint_handler.set as myset
import constraint_handler.utils.common as common

NO_ERRORS: tuple[tuple[warning.Kind, str], ...] = ()


K = typing.TypeVar("K")
V = typing.TypeVar("V")


class Multimap(Mapping[K, frozenset[V]]):
    def __init__(self, data: Mapping[K, frozenset[V]]):
        # Copy into a plain dict to decouple from caller mutability.
        self._data: dict[K, frozenset[V]] = dict(data)
        self._hash = hash(frozenset(self._data.items()))

    @classmethod
    def from_pairs(cls, pairs: typing.Iterable[tuple[K, V]]) -> "Multimap[K, V]":
        tmp: dict[K, set[V]] = {}
        for key, value in pairs:
            tmp.setdefault(key, set()).add(value)
        frozen = {key: frozenset(values) for key, values in tmp.items()}
        return cls(frozen)

    def __getitem__(self, key: K) -> frozenset[V]:
        return self._data[key]

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __hash__(self) -> int:
        return self._hash

    def __repr__(self):
        kv = ", ".join(f"{str(k)}:{str(v)}" for k, v in self._data.items())
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


def compare(multimap: Multimap, op: Callable):
    best_val = None
    errors: list[tuple[warning.Kind, typing.Any]] = []
    try:
        for key, value in multimap.items():
            local_best = op(value)
            if best_val is None:
                best_val = local_best
            elif local_best is not None:
                best_val = op(best_val, local_best)
    except TypeError as exn:
        errors.append(
            (
                warning.Expression(warning.ExpressionWarning.notImplemented),
                f"multimap does not support comparison of values of some types: {exn}",
            )
        )
    except Exception as exn:
        errors.append((warning.OtherError(), f"{exn}"))
    return best_val, errors


def evaluate_operator(o, args, apply_operator=None) -> atom.EvalResult:
    match o:
        case operators.MultimapOperator.multimap_isin:
            assert len(args) == 2
            return atom.EvalResult(args[0] in args[1], NO_ERRORS)
        case operators.MultimapOperator.find:
            assert len(args) == 2
            return atom.EvalResult(args[1][args[0]] if args[0] in args[1] else frozenset(), NO_ERRORS)
        case operators.MultimapOperator.find2:
            assert len(args) == 3
            return atom.EvalResult(args[1] in args[0] and args[2] in args[0][args[1]], NO_ERRORS)
        case operators.MultimapOperator.multimap_fold:
            if apply_operator is None:
                return atom.EvalResult(
                    common.Bad.bad,
                    ((warning.Expression(warning.ExpressionWarning.notImplemented), "multimap_fold missing callback"),),
                )
            fold_errors = []

            def step(*aaa):
                applied = apply_operator(args[0], aaa)
                fold_errors.extend(applied.errors)
                return applied.value

            return atom.EvalResult(fold(step, args[1], args[2]), tuple(fold_errors))
        case operators.MultimapOperator.multimap_fold_i:
            if apply_operator is None:
                return atom.EvalResult(
                    common.Bad.bad,
                    (
                        (
                            warning.Expression(warning.ExpressionWarning.notImplemented),
                            "multimap_fold_i missing callback",
                        ),
                    ),
                )
            fold_errors = []

            def step(*aaa):
                applied = apply_operator(args[0], aaa)
                fold_errors.extend(applied.errors)
                return applied.value

            return atom.EvalResult(fold_i(step, args[1], args[2]), tuple(fold_errors))
        case operators.MultimapOperator.multimap_make:
            return atom.EvalResult(Multimap.from_pairs(args), NO_ERRORS)
        case operators.MultimapOperator.countKeys:
            return atom.EvalResult(len(args[0]), NO_ERRORS)
        case operators.MultimapOperator.countEntries:
            count = 0
            for key, value in args[0].items():
                count += len(value)
            return atom.EvalResult(count, NO_ERRORS)
        case operators.MultimapOperator.sumIntEntries:
            total = 0
            for key, value in args[0].items():
                total += sum(v for v in value if isinstance(v, int))
            return atom.EvalResult(total, NO_ERRORS)
        case operators.MultimapOperator.maxEntries:
            __max, errors = compare(args[0], max)
            return atom.EvalResult(__max, tuple((kind, str(msg)) for kind, msg in errors))
        case operators.MultimapOperator.minEntries:
            __min, errors = compare(args[0], min)
            return atom.EvalResult(__min, tuple((kind, str(msg)) for kind, msg in errors))
        case _:
            return atom.EvalResult(
                common.Bad.bad,
                ((warning.Expression(warning.ExpressionWarning.notImplemented), f"multimap.operator {o}"),),
            )
