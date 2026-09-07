"""Convert Python values and typed records to and from Clingo symbols."""

import dataclasses
import enum
import itertools
import types
import typing
from functools import cache

import clingo


class FailedInstantiationExn(Exception):
    pass


def predicatedefn_default_predicate_name(name):
    return name[0].lower() + name[1:] if name else ""


def nest(l, cons="", nil=""):
    symb = clingo.Function(nil, [])
    for e in reversed(l):
        symb = clingo.Function(cons, [e, symb])
    return symb


def unnest(symb, cons="", nil=""):
    l = []
    s = symb
    while True:
        if s.type == clingo.SymbolType.Function and s.name == cons and len(s.arguments) == 2:
            l.append(s.arguments[0])
            s = s.arguments[1]
        elif s.type == clingo.SymbolType.Function and s.name == nil and len(s.arguments) == 0:
            return l
        else:
            raise FailedInstantiationExn(f"{symb} is not a list")


class ImmutableList(tuple):
    def __new__(cls, values=()):
        return super().__new__(cls, values)

    def __repr__(self):
        return f"{type(self).__name__}({list(self)!r})"

    @classmethod
    def pytocl(cls, value, target_args=()):
        subtarget = target_args[0] if target_args else None
        if subtarget is not None:
            return nest([pytocl(e, subtarget) for e in value])
        return nest([pytocl(e) for e in value])

    @classmethod
    def cltopy(cls, func, target_args=()):
        subtarget = target_args[0] if target_args else None
        un = unnest(func)
        if subtarget is not None:
            return cls(cltopy(e, subtarget) for e in un)
        return cls(un)


baseTypes = {"bool": bool, "int": int, "float": float, "string": str, "none": type(None)}
_NO_CUSTOM_CONVERTER = object()


@cache
def _resolve_type_alias(target):
    while isinstance(target, typing.TypeAliasType):
        target = target.__value__
    return target


@cache
def _cached_get_origin(target):
    return typing.get_origin(target)


@cache
def _cached_get_args(target):
    return typing.get_args(target)


@cache
def _cached_get_type_hints(target):
    return typing.get_type_hints(target)


def _substitute_typevars(target, typevars):
    if target in typevars:
        return typevars[target]
    origin = _cached_get_origin(target)
    type_args = _cached_get_args(target)
    if not type_args:
        return target
    type_args = tuple(_substitute_typevars(arg, typevars) for arg in type_args)
    if origin in (typing.Union, types.UnionType):
        return typing.Union[type_args]
    return origin[type_args]


@cache
def _get_record_predicate_name(target):
    return predicatedefn_default_predicate_name(target.__name__)


def _get_signatures(target):
    target_class = _cached_get_origin(target) or target
    if dataclasses.is_dataclass(target_class):
        arity = sum(field.init for field in dataclasses.fields(target_class))
    elif getattr(target_class, "_fields", None) is not None:
        arity = len(target_class._fields)
    elif isinstance(target_class, type):
        arity = len(_cached_get_type_hints(target_class))
    else:
        raise ValueError("not sure what to do with target", target)
    return ((_get_record_predicate_name(target_class), arity),)


@cache
def _union_rows(target):
    target = _resolve_type_alias(target)
    origin = _cached_get_origin(target)
    if origin in (typing.Union, types.UnionType):
        return _cached_get_args(target)
    return (target,)


def _resolve_custom_converter(target, name, value):
    origin = _cached_get_origin(target)
    target_args = _cached_get_args(target)
    converters = [
        converter
        for candidate in (target, origin)
        if candidate is not None
        for converter in [getattr(candidate, name, None)]
        if converter is not None
    ]
    for converter in converters:
        try:
            return converter(value, target_args=target_args)
        except TypeError:
            return converter(value)
    return _NO_CUSTOM_CONVERTER


def pytocl(v, target_type=None):
    """Encode a Python value as a Clingo symbol.

    Dataclasses, NamedTuples, and annotated classes use their lower-camel-case
    class name as the predicate name. ``target_type`` selects a type or union.

    >>> symbol = pytocl([1, "two", 3])
    >>> print(symbol)
    (1,("two",(3,())))
    """
    if target_type is None:
        target_type = type(v)

    if target_type is int:
        return clingo.Number(v)
    if target_type is bool:
        return clingo.Function("true" if v else "false", [])
    if target_type is str:
        return clingo.String(v)
    if target_type is float:
        return clingo.Function("float", [clingo.String(str(v))])
    if target_type is types.NoneType or target_type is type(None):
        return clingo.Function("none", [])
    if target_type is list:
        return nest([pytocl(e) for e in v])
    if target_type is tuple:
        return clingo.Function("", [pytocl(e) for e in v])
    if target_type is set or target_type is frozenset:
        return clingo.Function("set", [nest(sorted([pytocl(e) for e in v]))])
    if target_type is clingo.Symbol:
        return v

    rows = _union_rows(target_type)
    for target in rows:
        target = _resolve_type_alias(target)
        target_class = _cached_get_origin(target) or target
        custom_value = _resolve_custom_converter(target, "pytocl", v)
        if custom_value is not _NO_CUSTOM_CONVERTER:
            return custom_value
        if target_class == typing.Any:
            return v
        if not isinstance(target_class, type) or not isinstance(v, target_class):
            continue
        if issubclass(target_class, clingo.Symbol):
            return v
        elif issubclass(target_class, enum.Enum):
            symbol_name = v.value if isinstance(v.value, str) else predicatedefn_default_predicate_name(v.name)
            return clingo.Function(symbol_name, [])
        elif target_class == types.NoneType:
            return clingo.Function("none", [])
        elif issubclass(target_class, bool):
            return clingo.Function("true" if v else "false", [])
        elif issubclass(target_class, int):
            return clingo.Number(v)
        elif issubclass(target_class, str):
            return clingo.String(v)
        elif issubclass(target_class, float):
            return clingo.Function("float", [clingo.String(str(v))])
        elif issubclass(target_class, list):
            return nest([pytocl(e) for e in v])
        elif issubclass(target_class, set) or issubclass(target_class, frozenset):
            return clingo.Function("set", [nest(sorted([pytocl(e) for e in v]))])
        elif dataclasses.is_dataclass(target_class):
            name = _get_record_predicate_name(target_class)
            fields = (field for field in dataclasses.fields(target_class) if field.init)
            return clingo.Function(name, [pytocl(getattr(v, field.name)) for field in fields])
        elif getattr(target_class, "_fields", None) is not None:
            assert getattr(target_class, "__name__", None) is not None
            name = _get_record_predicate_name(target_class)
            field_values = [pytocl(getattr(v, field)) for field in target_class._fields]
            return clingo.Function(name, field_values)
        elif issubclass(target_class, tuple):
            return clingo.Function("", [pytocl(e) for e in v])
        else:
            name = _get_record_predicate_name(target_class)
            field_types = _cached_get_type_hints(target_class)
            return clingo.Function(name, [pytocl(getattr(v, name), field) for name, field in field_types.items()])
    raise FailedInstantiationExn(f"'{v}' is not of type {target_type}")


def cltopyNoTarget(func: clingo.Symbol) -> object:
    try:
        if func.type not in [clingo.SymbolType.Number, clingo.SymbolType.String, clingo.SymbolType.Function]:
            raise NotImplementedError(func.type)  # [clingo.SymbolType.Infimum, clingo.SymbolType.Supremum]:
        if func.type == clingo.SymbolType.Number:
            return func.number
        elif func.type == clingo.SymbolType.String:
            return func.string
        elif (
            func.name == "float"
            and len(func.arguments) == 1
            and func.arguments[0].type in [clingo.SymbolType.String, clingo.SymbolType.Number]
        ):
            arg = func.arguments[0]
            return float(arg.string if arg.type == clingo.SymbolType.String else arg.number)
        elif func.name in ["true", "false"] and len(func.arguments) == 0:
            return func.name == "true"
        elif func.name == "none" and len(func.arguments) == 0:
            return None
        elif func.name == "set" and len(func.arguments) == 1:
            l = unnest(func.arguments[0])
            return frozenset(cltopyNoTarget(e) for e in l)
        elif func.name == "":
            try:
                l = unnest(func)
                return ImmutableList([cltopyNoTarget(e) for e in l])
            except FailedInstantiationExn:
                return tuple([cltopyNoTarget(e) for e in func.arguments])
        else:
            return func
    except FailedInstantiationExn:
        return func


@cache
def cltopy(func, target_type=typing.Any):
    """Decode a Clingo symbol as ``target_type`` or one of its union members.

    >>> symbol = clingo.symbol.parse_term('(1,("two",(3,())))')
    >>> cltopy(symbol, list[int | str])
    ImmutableList([1, 'two', 3])
    """
    target_type = _resolve_type_alias(target_type)
    rows = _union_rows(target_type)
    for target in rows:
        target = _resolve_type_alias(target)
        target_class = _cached_get_origin(target) or target  # unsubscripted_target
        try:
            if target == typing.Any:
                return func
            custom_value = _resolve_custom_converter(target, "cltopy", func)
            if custom_value is not _NO_CUSTOM_CONVERTER:
                return custom_value
            elif dataclasses.is_dataclass(target_class):
                if func.type == clingo.SymbolType.Function:
                    name = _get_record_predicate_name(target_class)
                    init_fields = tuple(field for field in dataclasses.fields(target_class) if field.init)
                    field_types = _cached_get_type_hints(target_class)
                    typevars = dict(zip(getattr(target_class, "__parameters__", ()), _cached_get_args(target)))
                    if name == func.name and len(init_fields) == len(func.arguments):
                        keyword_args = {
                            field.name: cltopy(
                                symb, _substitute_typevars(field_types.get(field.name, typing.Any), typevars)
                            )
                            for symb, field in zip(func.arguments, init_fields)
                        }
                        try:
                            return target_class(**keyword_args)
                        except TypeError as error:
                            raise FailedInstantiationExn(str(error)) from error
            elif getattr(target_class, "_fields", None) is not None:
                if func.type == clingo.SymbolType.Function:  # NamedTuple
                    name = _get_record_predicate_name(target_class)
                    field_types = _cached_get_type_hints(target_class)
                    typevars = dict(zip(getattr(target_class, "__parameters__", ()), _cached_get_args(target)))
                    if name == func.name and len(target_class._fields) == len(func.arguments):
                        field_values = (
                            cltopy(symb, _substitute_typevars(field_types.get(field, typing.Any), typevars))
                            for symb, field in zip(func.arguments, target_class._fields)
                        )
                        return target_class(*field_values)
            elif any(isinstance(target_class, t) for t in list(baseTypes.values()) + [list, clingo.Symbol]):
                if cltopy(func) == target:
                    return target
            elif isinstance(target_class, type):
                if issubclass(target_class, clingo.Symbol):
                    return func
                elif issubclass(target_class, enum.Enum):
                    if func.type == clingo.SymbolType.Function and len(func.arguments) == 0:
                        for member in target_class:
                            if (
                                member.name == func.name
                                or predicatedefn_default_predicate_name(member.name) == func.name
                            ):
                                return member
                            if isinstance(member.value, str) and member.value == func.name:
                                return member
                elif issubclass(target_class, bool):
                    if (
                        func.type == clingo.SymbolType.Function
                        and func.name in ["true", "false"]
                        and len(func.arguments) == 0
                    ):
                        return func.name == "true"
                elif issubclass(target_class, int):
                    if func.type == clingo.SymbolType.Number:
                        return func.number
                elif issubclass(target_class, str):
                    if func.type == clingo.SymbolType.String:
                        return func.string
                elif issubclass(target_class, float):
                    if (
                        func.type == clingo.SymbolType.Function
                        and func.name == "float"
                        and len(func.arguments) == 1
                        and func.arguments[0].type in [clingo.SymbolType.String, clingo.SymbolType.Number]
                    ):
                        arg = func.arguments[0]
                        return float(arg.string if arg.type == clingo.SymbolType.String else arg.number)
                elif issubclass(target_class, type(None)):
                    if func.name == "none" and len(func.arguments) == 0:
                        return None
                elif issubclass(target_class, list):
                    subtarget = _cached_get_args(target)
                    elements = unnest(func)
                    if subtarget:
                        return ImmutableList(cltopy(element, subtarget[0]) for element in elements)
                    return ImmutableList(elements)
                elif issubclass(target_class, set) or issubclass(target_class, frozenset):
                    subtarget = _cached_get_args(target)
                    if func.type == clingo.SymbolType.Function and func.name == "set" and len(func.arguments) == 1:
                        elements = unnest(func.arguments[0])
                        if subtarget:
                            return frozenset(cltopy(element, subtarget[0]) for element in elements)
                        return frozenset(elements)
                elif issubclass(target_class, tuple):
                    subtargets = _cached_get_args(target)
                    if len(subtargets) >= 2 and subtargets[-1] == Ellipsis and func.type == clingo.SymbolType.Function:
                        subtargets = subtargets[:-1] + tuple(subtargets[-2] for _ in range(len(func.arguments) - 1))
                    if (
                        func.type == clingo.SymbolType.Function
                        and func.name == ""
                        and len(subtargets) <= len(func.arguments)
                    ):
                        symbols_and_targets = itertools.zip_longest(func.arguments, subtargets)
                        return tuple(cltopy(symb, subt) for (symb, subt) in symbols_and_targets)
                elif func.type == clingo.SymbolType.Function:
                    name = _get_record_predicate_name(target_class)
                    field_types = _cached_get_type_hints(target_class)
                    if name == func.name and len(field_types) == len(func.arguments):
                        return target_class(
                            **{
                                field_name: cltopy(symb, field_type)
                                for symb, (field_name, field_type) in zip(func.arguments, field_types.items())
                            }
                        )
            raise FailedInstantiationExn(f"'{func}' is not of type '{target}'")
        except FailedInstantiationExn:
            pass
    raise FailedInstantiationExn(f"'{func}' is not of type {target_type}")


def findInModel(
    model: clingo.Model, target_type: typing.Any = typing.Any, atoms: bool = True, theory: bool = True
) -> dict[clingo.Symbol, typing.Any]:
    """Return model symbols that decode as ``target_type``."""
    rows = _union_rows(target_type)
    result = dict()
    for target in rows:
        for symb in model.symbols(atoms=atoms, theory=theory):
            try:
                v = cltopy(symb, target)
                result[symb] = v
            except FailedInstantiationExn:
                pass
    return result


def _find_in_control(
    ctl: clingo.Control | clingo.propagator.PropagateInit, target_type: typing.Any
) -> typing.Iterator[tuple[clingo.SymbolicAtom, typing.Any]]:
    rows = _union_rows(target_type)
    if typing.Any in rows:
        for atom in ctl.symbolic_atoms:
            yield atom, atom.symbol
    for target in rows:
        if target != typing.Any:
            for name, arity in _get_signatures(target):
                for atom in ctl.symbolic_atoms.by_signature(name, arity):
                    try:
                        yield atom, cltopy(atom.symbol, target)
                    except FailedInstantiationExn:
                        pass


def findInControl(ctl: clingo.Control, target_type: typing.Any) -> dict[clingo.SymbolicAtom, typing.Any]:
    """Return control atoms that decode as ``target_type``."""
    return dict(_find_in_control(ctl, target_type))


def findInPropagateInit(ctl: clingo.propagator.PropagateInit, target_type: typing.Any) -> dict[typing.Any, int]:
    """Return decoded propagator atoms mapped to their solver literals."""
    result = dict()
    for atom, value in _find_in_control(ctl, target_type):
        literal = ctl.solver_literal(atom.literal)
        if literal != -1:
            result[value] = literal
    return result
