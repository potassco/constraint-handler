"""Private result inference and shared operator contracts."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from itertools import product
from typing import TYPE_CHECKING, Literal

from ..analysis import LINEAR_RELATIONS
from ..internal_input import (
    ConstraintStore,
    Expr,
    Lambda,
    Operation,
    OperationArg,
    Python,
    ValueDef,
    ValueType,
    VariableRef,
)
from ..python_input import Operator
from .type_cache import (
    UNKNOWN,
    SetOf,
    TupleType,
    Type,
    TypeMember,
    UnknownType,
    union_types,
)

if TYPE_CHECKING:
    from .type_cache import TypeCache

__all__ = [
    "_TypeInference",
    "lambda_bindings",
    "operation_errors",
    "operation_warnings",
    "scalar_subset",
]

_NUMERIC = frozenset({ValueType.integer, ValueType.real})
_BOOLEAN = frozenset({ValueType.boolean})
_INTEGER = frozenset({ValueType.integer})


@dataclass(frozen=True)
class _Rule:
    """Keep arity, uniform scalar contracts, and fixed result types together."""

    minimum: int
    maximum: int | None
    result: Type | None = None
    scalars: frozenset[ValueType] | None = None
    shape: Literal["set", "tuple"] | None = None


_RULES: dict[Operator, _Rule] = {
    **dict.fromkeys((Operator.eq, Operator.neq), _Rule(2, 2, _BOOLEAN)),
    **dict.fromkeys(
        (Operator.lt, Operator.leq, Operator.gt, Operator.geq),
        _Rule(2, 2, _BOOLEAN, _NUMERIC),
    ),
    **dict.fromkeys(
        (Operator.conj, Operator.disj, Operator.lxor, Operator.leqv),
        _Rule(0, None, _BOOLEAN, _BOOLEAN),
    ),
    Operator.limp: _Rule(2, 2, _BOOLEAN, _BOOLEAN),
    Operator.lnot: _Rule(1, 1, _BOOLEAN, _BOOLEAN),
    **dict.fromkeys(
        (Operator.snot, Operator.wnot),
        _Rule(1, 1, _BOOLEAN, _BOOLEAN | {ValueType.none}),
    ),
    Operator.has_value: _Rule(1, 1, _BOOLEAN),
    **dict.fromkeys(
        (Operator.set_isin, Operator.set_notin, Operator.subset), _Rule(2, 2, _BOOLEAN)
    ),
    Operator.linear_comparison: _Rule(2, None, _BOOLEAN),
    Operator.length: _Rule(1, 1, _INTEGER),
    Operator.cardinality: _Rule(1, 1, _INTEGER),
    **dict.fromkeys((Operator.floor, Operator.ceil), _Rule(1, 1, _INTEGER, _NUMERIC)),
    Operator.int_div: _Rule(2, 2, _INTEGER, _NUMERIC),
    Operator.linear_integer: _Rule(0, None, _INTEGER),
    Operator.int_from_real: _Rule(1, 1, _INTEGER, frozenset({ValueType.real})),
    **dict.fromkeys(
        (
            Operator.sqrt,
            Operator.sin,
            Operator.cos,
            Operator.tan,
            Operator.asin,
            Operator.acos,
            Operator.atan,
        ),
        _Rule(1, 1, _NUMERIC, _NUMERIC),
    ),
    Operator.real_div: _Rule(2, 2, _NUMERIC, _NUMERIC),
    Operator.concat: _Rule(
        2, 2, frozenset({ValueType.string}), frozenset({ValueType.string})
    ),
    Operator.real_from_int: _Rule(1, 1, frozenset({ValueType.real}), _INTEGER),
    **dict.fromkeys((Operator.abs, Operator.minus), _Rule(1, 1, scalars=_NUMERIC)),
    **dict.fromkeys(
        (Operator.add, Operator.sub, Operator.mult, Operator.mod, Operator.pow),
        _Rule(2, 2, scalars=_NUMERIC),
    ),
    **dict.fromkeys((Operator.min, Operator.max), _Rule(1, None, scalars=_NUMERIC)),
    **dict.fromkeys(
        (Operator.get_or_else, Operator.if_, Operator.tuple_get), _Rule(2, 2)
    ),
    Operator.ite: _Rule(3, 3),
    **dict.fromkeys((Operator.set_make, Operator.union), _Rule(0, None, shape="set")),
    Operator.make_tuple: _Rule(0, None, shape="tuple"),
    Operator.inter: _Rule(1, None, shape="set"),
    Operator.diff: _Rule(2, 2, shape="set"),
    Operator.set_fold: _Rule(3, 3),
    **dict.fromkeys((Operator.lambda_, Operator.python_eval), _Rule(1, None)),
}


class _TypeInference:
    """Compute result approximations through the owning cache only."""

    def __init__(self, types: TypeCache, store: ConstraintStore) -> None:
        """Retain the session cache and its stable store context."""
        self._types = types
        self._store = store

    def compute(self, expr: Expr, bindings: Mapping[VariableRef, Type]) -> Type:
        """Infer a value expression without checking validity or definedness."""
        match expr:
            case ValueDef(kind, _):
                return frozenset({kind})
            case VariableRef():
                if expr in bindings:
                    return bindings[expr]
                return self._types.get_type(expr) if bindings else self._variable(expr)
            case tuple():
                return self._tuple(expr, bindings)
            case frozenset():
                return self._set(expr, bindings)
            case Operation(op, args):
                fixed = _RULES[op].result
                if fixed is not None:
                    return fixed
                if op == Operator.python_eval or op == Operator.set_fold:
                    return UNKNOWN
                if op == Operator.lambda_:
                    if not args or not isinstance(args[0], Lambda):
                        return UNKNOWN
                    callback = args[0]
                    if len(callback.vars) != len(args) - 1 or len(
                        set(callback.vars)
                    ) != len(callback.vars):
                        return UNKNOWN
                    kinds = [self.argument_type(arg, bindings) for arg in args[1:]]
                    return union_types(
                        self._types.get_type(callback.expr, local)
                        for local in lambda_bindings(callback, kinds, bindings)
                    )
                if op == Operator.make_tuple:
                    return self._tuple(args, bindings)
                if op == Operator.set_make:
                    return self._set(args, bindings)
                if op in {Operator.ite, Operator.if_, Operator.get_or_else}:
                    if op == Operator.if_ and len(args) == 2:
                        return union_types(
                            (
                                self.argument_type(args[1], bindings),
                                frozenset({ValueType.none}),
                            )
                        )
                    if op == Operator.ite and len(args) == 3:
                        return union_types(
                            self.argument_type(arg, bindings) for arg in args[1:]
                        )
                    if op == Operator.get_or_else and len(args) == 2:
                        first = self.argument_type(args[0], bindings)
                        if isinstance(first, UnknownType):
                            return UNKNOWN
                        if ValueType.none not in first:
                            return first
                        return union_types(
                            (
                                first - {ValueType.none},
                                self.argument_type(args[1], bindings),
                            )
                        )
                    return UNKNOWN
                kinds = [self.argument_type(arg, bindings) for arg in args]
                if any(isinstance(kind, UnknownType) for kind in kinds):
                    return UNKNOWN
                known = [kind for kind in kinds if not isinstance(kind, UnknownType)]
                if op in {
                    Operator.abs,
                    Operator.minus,
                    Operator.add,
                    Operator.sub,
                    Operator.mult,
                    Operator.mod,
                    Operator.pow,
                    Operator.min,
                    Operator.max,
                }:
                    if not known or any(not kind <= _NUMERIC for kind in known):
                        return UNKNOWN
                    if any(not kind for kind in known):
                        return frozenset()
                    if op in {Operator.abs, Operator.minus}:
                        return known[0] if len(known) == 1 else UNKNOWN
                    if op in {Operator.min, Operator.max}:
                        return union_types(known)
                    if len(known) != 2:
                        return UNKNOWN
                    if op == Operator.pow:
                        return _NUMERIC
                    members: set[ValueType] = set()
                    if all(ValueType.integer in kind for kind in known):
                        members.add(ValueType.integer)
                    if any(ValueType.real in kind for kind in known):
                        members.add(ValueType.real)
                    return frozenset(members)
                if op in {Operator.union, Operator.inter, Operator.diff}:
                    if not known:
                        return (
                            frozenset({SetOf(frozenset(), True)})
                            if op == Operator.union
                            else UNKNOWN
                        )
                    if any(not kind for kind in known):
                        return frozenset()
                    if any(
                        not isinstance(member, SetOf)
                        for kind in known
                        for member in kind
                    ):
                        return UNKNOWN
                    sets = [
                        member
                        for kind in known
                        for member in kind
                        if isinstance(member, SetOf)
                    ]
                    elements = frozenset(
                        element for member in sets for element in member.elements
                    )
                    if op == Operator.diff:
                        if len(known) != 2:
                            return UNKNOWN
                        elements = frozenset(
                            element
                            for member in known[0]
                            if isinstance(member, SetOf)
                            for element in member.elements
                        )
                    return frozenset(
                        {
                            SetOf(
                                elements,
                                op != Operator.union
                                or all(member.can_be_empty for member in sets),
                            )
                        }
                    )
                if op == Operator.tuple_get:
                    if len(known) != 2 or not known[1] <= _INTEGER:
                        return UNKNOWN
                    if any(not kind for kind in known):
                        return frozenset()
                    if any(not isinstance(member, TupleType) for member in known[0]):
                        return UNKNOWN
                    tuples = [
                        member for member in known[0] if isinstance(member, TupleType)
                    ]
                    index = args[1]
                    if (
                        isinstance(index, ValueDef)
                        and index.value_type == ValueType.integer
                        and isinstance(index.value, int)
                    ):
                        if any(
                            not 0 <= index.value < len(member.elements)
                            for member in tuples
                        ):
                            return UNKNOWN
                        return union_types(
                            member.elements[index.value] for member in tuples
                        )
                    return union_types(
                        position for member in tuples for position in member.elements
                    )
                return UNKNOWN
            case _:
                raise TypeError("get_type requires a value expression")

    def argument_type(
        self, arg: OperationArg, bindings: Mapping[VariableRef, Type]
    ) -> Type:
        """Request a value argument's type, leaving callable descriptors unknown."""
        if isinstance(arg, (Lambda, Python)):
            return UNKNOWN
        return self._types.get_type(arg, bindings)

    def _tuple(
        self, args: tuple[OperationArg, ...], bindings: Mapping[VariableRef, Type]
    ) -> Type:
        """Preserve tuple positions without permitting nested tuple alternatives."""
        kinds = tuple(self.argument_type(arg, bindings) for arg in args)
        if any(
            isinstance(member, TupleType)
            for kind in kinds
            if not isinstance(kind, UnknownType)
            for member in kind
        ):
            return UNKNOWN
        if any(not kind for kind in kinds):
            return frozenset()
        return frozenset({TupleType(kinds)})

    def _set(
        self, args: Iterable[OperationArg], bindings: Mapping[VariableRef, Type]
    ) -> Type:
        """Infer scalar set elements conservatively without filtering invalid unions."""
        kinds = [self.argument_type(arg, bindings) for arg in args]
        if any(isinstance(kind, UnknownType) for kind in kinds):
            return UNKNOWN
        known = [kind for kind in kinds if not isinstance(kind, UnknownType)]
        if any(not kind for kind in known):
            return frozenset()
        if any(not isinstance(member, ValueType) for kind in known for member in kind):
            return UNKNOWN
        return frozenset(
            {
                SetOf(
                    frozenset(
                        member
                        for kind in known
                        for member in kind
                        if isinstance(member, ValueType)
                    ),
                    not kinds,
                )
            }
        )

    def _variable(self, variable: VariableRef) -> Type:
        """Combine declared sources, distinguishing undeclared and empty variables."""
        kinds: list[Type] = []
        if (
            variable not in self._store.variables
            and variable not in self._store.set_variables
        ):
            return UNKNOWN
        if variable in self._store.variables:
            definition = self._store.variables[variable]
            kinds.extend(
                self._types.get_type(self._store.expressions[source.value])
                for source in (
                    *definition.choices,
                    *definition.definitions,
                    *definition.defaults,
                )
            )
        if variable in self._store.set_variables:
            set_definition = self._store.set_variables[variable]
            sources = [
                self._types.get_type(self._store.expressions[source.value])
                for source in (
                    *set_definition.bases,
                    *set_definition.assigns,
                    *set_definition.defaults,
                )
            ]
            elements = union_types(sources)
            if isinstance(elements, UnknownType) or any(
                not isinstance(member, ValueType) for member in elements
            ):
                kinds.append(UNKNOWN)
            else:
                can_be_empty = not any(
                    self._store.expressions[source.condition]
                    == ValueDef(ValueType.boolean, True)
                    for source in set_definition.assigns
                )
                kinds.append(
                    frozenset(
                        {
                            SetOf(
                                frozenset(
                                    member
                                    for member in elements
                                    if isinstance(member, ValueType)
                                ),
                                can_be_empty,
                            )
                        }
                    )
                )
        return union_types(kinds)


def lambda_bindings(
    callback: Lambda, kinds: list[Type], outer: Mapping[VariableRef, Type]
) -> Iterable[dict[VariableRef, Type]]:
    """Extend lexical bindings for every argument alternative, including unknowns."""
    alternatives = [
        (kind,)
        if isinstance(kind, UnknownType)
        else tuple(frozenset({member}) for member in kind)
        for kind in kinds
    ]
    for combination in product(*alternatives):
        local = dict(outer)
        local.update(dict.fromkeys(callback.vars, UNKNOWN))
        local.update(zip(callback.vars, combination, strict=True))
        yield local


def scalar_subset(kind: Type, allowed: frozenset[ValueType]) -> bool:
    """Accept unknowns while requiring every known alternative to be allowed."""
    return isinstance(kind, UnknownType) or all(
        isinstance(member, ValueType) and member in allowed for member in kind
    )


def operation_errors(expression: Operation, kinds: list[Type]) -> Iterable[str]:
    """Validate operator contracts independently of their inferred result types."""
    op, args = expression.op, expression.args
    rule = _RULES[op]
    if (
        len(args) < rule.minimum
        or rule.maximum is not None
        and len(args) > rule.maximum
    ):
        yield f"{op} has invalid arity: got {len(args)}"
    if rule.scalars is not None and any(
        not scalar_subset(kind, rule.scalars) for kind in kinds
    ):
        yield f"{op} requires {'/'.join(sorted(rule.scalars))} arguments"
    known: list[frozenset[TypeMember]] = [
        frozenset() if isinstance(kind, UnknownType) else kind for kind in kinds
    ]
    if (
        op in {Operator.if_, Operator.ite}
        and kinds
        and not scalar_subset(kinds[0], _BOOLEAN)
    ):
        yield f"{op} requires a Boolean condition"
    shapes = [
        "tuple"
        if isinstance(arg, tuple)
        else "set"
        if isinstance(arg, frozenset)
        else _RULES[arg.op].shape
        if isinstance(arg, Operation)
        else None
        for arg in args
    ]
    if op == Operator.make_tuple and (
        "tuple" in shapes
        or any(isinstance(member, TupleType) for kind in known for member in kind)
    ):
        yield "Nested tuples are not supported"
    if op == Operator.set_make and (
        any(shape is not None for shape in shapes)
        or any(not isinstance(member, ValueType) for kind in known for member in kind)
    ):
        yield "set_make requires scalar arguments"
    if op in {
        Operator.union,
        Operator.inter,
        Operator.diff,
        Operator.subset,
        Operator.cardinality,
    } and any(not isinstance(member, SetOf) for kind in known for member in kind):
        yield f"{op} requires set arguments"
    if op in {Operator.set_isin, Operator.set_notin}:
        if known and (
            shapes[0] is not None or not scalar_subset(kinds[0], frozenset(ValueType))
        ):
            yield f"{op} requires a scalar element"
        if len(known) > 1 and any(not isinstance(member, SetOf) for member in known[1]):
            yield f"{op} requires a set as second argument"
    if (
        op == Operator.length
        and known
        and any(
            member != ValueType.string and not isinstance(member, (SetOf, TupleType))
            for member in known[0]
        )
    ):
        yield "length requires a string, tuple, or set argument"
    if op == Operator.tuple_get:
        if known and any(not isinstance(member, TupleType) for member in known[0]):
            yield "tuple_get first argument must be a tuple"
        if len(kinds) > 1 and not scalar_subset(kinds[1], _INTEGER):
            yield "tuple_get index must be an integer"
    if op in {Operator.lambda_, Operator.set_fold} and args:
        if not isinstance(args[0], Lambda):
            yield f"{op} requires a Lambda as first argument"
        elif len(set(args[0].vars)) != len(args[0].vars):
            yield "Lambda parameter names must be distinct"
        if (
            op == Operator.set_fold
            and len(known) > 1
            and any(not isinstance(member, SetOf) for member in known[1])
        ):
            yield "set_fold requires a set as second argument"
    if op == Operator.python_eval and args and not isinstance(args[0], Python):
        yield "python_eval requires a Python callable as first argument"
    if op in {Operator.linear_integer, Operator.linear_comparison}:
        start = 1 if op == Operator.linear_comparison else 0
        if (
            start
            and args
            and (
                not isinstance(args[0], ValueDef)
                or args[0].value_type != ValueType.string
                or args[0].value not in LINEAR_RELATIONS
            )
        ):
            yield "linear_comparison requires a literal relation: eq, neq, lt, leq, gt, geq"
        linear = args[start:]
        if linear:
            offset = linear[-1]
            if (
                not isinstance(offset, ValueDef)
                or offset.value_type != ValueType.integer
                or type(offset.value) is not int
            ):
                yield "linear_integer constant offset must be a constant integer literal"
            for index, arg in enumerate(linear[:-1], start=start):
                if not isinstance(arg, tuple) or len(arg) != 2:
                    yield "linear_integer requires coefficient/term pairs"
                    continue
                coefficient = arg[0]
                if (
                    not isinstance(coefficient, ValueDef)
                    or coefficient.value_type != ValueType.integer
                    or type(coefficient.value) is not int
                ):
                    yield "linear_integer coefficient must be a constant integer literal"
                for member in known[index]:
                    if isinstance(member, TupleType) and not scalar_subset(
                        member.elements[1], _INTEGER
                    ):
                        yield "linear_integer terms must be integer"


def operation_warnings(expression: Operation, kinds: list[Type]) -> Iterable[str]:
    """Report equality warnings for incompatible known alternatives only."""
    if expression.op not in {Operator.eq, Operator.neq} or len(kinds) != 2:
        return
    known: list[frozenset[TypeMember]] = [
        frozenset() if isinstance(kind, UnknownType) else kind for kind in kinds
    ]
    for left, right in product(*known):
        left_kind: ValueType | type[SetOf | TupleType] = (
            left if isinstance(left, ValueType) else type(left)
        )
        right_kind: ValueType | type[SetOf | TupleType] = (
            right if isinstance(right, ValueType) else type(right)
        )
        if left_kind != right_kind and not (
            isinstance(left, ValueType)
            and isinstance(right, ValueType)
            and {left, right} <= _NUMERIC
        ):
            yield "Comparing values of different types"
            return
