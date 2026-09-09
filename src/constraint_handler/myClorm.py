"""Convert Python values and typed records to and from Clingo symbols."""

import dataclasses
import enum
import types
import typing
from functools import cache

import clingo

TRUE = clingo.Function("true", [])
FALSE = clingo.Function("false", [])
NONE = clingo.Function("none", [])


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


_NO_CUSTOM_CONVERTER = object()
_cltopy_cache = {}


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


@cache
def _get_record_field_targets(target, target_class):
    fields = getattr(target_class, "_fields", None)
    if fields is None:
        if dataclasses.is_dataclass(target_class):
            fields = tuple(field.name for field in dataclasses.fields(target_class) if field.init)
        else:
            fields = _cached_get_type_hints(target_class)
    field_types = _cached_get_type_hints(target_class)
    typevars = dict(zip(getattr(target_class, "__parameters__", ()), _cached_get_args(target)))
    return {field: _substitute_typevars(field_types.get(field, typing.Any), typevars) for field in fields}


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
    while _cached_get_origin(target) is typing.Annotated:
        target = _resolve_type_alias(_cached_get_args(target)[0])
    origin = _cached_get_origin(target)
    if origin in (typing.Union, types.UnionType):
        return tuple(_resolve_type_alias(member) for member in _cached_get_args(target))
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

    for target in _union_rows(target_type):
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
            return NONE
        elif issubclass(target_class, bool):
            return TRUE if v else FALSE
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
        elif func in (TRUE, FALSE):
            return func == TRUE
        elif func == NONE:
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


def cltopy(func, target_type=typing.Any):
    """Decode a Clingo symbol as ``target_type`` or one of its union members.

    >>> symbol = clingo.symbol.parse_term('(1,("two",(3,())))')
    >>> cltopy(symbol, list[int | str])
    ImmutableList([1, 'two', 3])
    """
    tasks = [("decode", func, target_type)]
    values = []
    while tasks:
        kind, *task = tasks.pop()
        if kind == "build":
            cache_key, target, size, fields = task
            children = values[-size:] if size else []
            if size:
                del values[-size:]
            values.append(target(children) if fields is None else target(**dict(zip(fields, children))))
            continue
        if kind == "cache":
            _cltopy_cache[task[0]] = values[-1]
            continue

        symbol, target_type = task
        cache_key = (symbol, target_type)
        if cache_key in _cltopy_cache:
            values.append(_cltopy_cache[cache_key])
            continue
        tasks.append(("cache", cache_key))
        for target in _union_rows(target_type):
            if _cached_get_origin(target) in (typing.Union, types.UnionType):
                tasks.append(("decode", symbol, target))
                break
            target_class = _cached_get_origin(target) or target
            if target == typing.Any:
                values.append(symbol)
                break
            if not isinstance(target_class, type):
                continue
            if target_class not in (list, ImmutableList, set, frozenset, tuple):
                custom_value = _resolve_custom_converter(target, "cltopy", symbol)
                if custom_value is not _NO_CUSTOM_CONVERTER:
                    values.append(custom_value)
                    break
            if issubclass(target_class, clingo.Symbol):
                values.append(symbol)
                break
            if issubclass(target_class, bool):
                if symbol not in (TRUE, FALSE):
                    continue
                values.append(symbol == TRUE)
                break
            elif issubclass(target_class, int) and symbol.type == clingo.SymbolType.Number:
                values.append(symbol.number)
                break
            elif issubclass(target_class, str) and symbol.type == clingo.SymbolType.String:
                values.append(symbol.string)
                break
            elif issubclass(target_class, float):
                if symbol.type == clingo.SymbolType.Function and symbol.name == "float" and len(symbol.arguments) == 1:
                    arg = symbol.arguments[0]
                    if arg.type in [clingo.SymbolType.String, clingo.SymbolType.Number]:
                        values.append(float(arg.string if arg.type == clingo.SymbolType.String else arg.number))
                        break
            elif issubclass(target_class, type(None)):
                if symbol == NONE:
                    values.append(None)
                    break
            if symbol.type != clingo.SymbolType.Function:
                continue
            if issubclass(target_class, enum.Enum) and not symbol.arguments:
                for member in target_class:
                    if member.name == symbol.name or predicatedefn_default_predicate_name(member.name) == symbol.name:
                        values.append(member)
                        break
                    if isinstance(member.value, str) and member.value == symbol.name:
                        values.append(member)
                        break
                else:
                    continue
                break
            if issubclass(target_class, (list, ImmutableList)):
                elements, container = unnest(symbol), ImmutableList
            elif issubclass(target_class, (set, frozenset)) and symbol.name == "set" and len(symbol.arguments) == 1:
                elements, container = unnest(symbol.arguments[0]), frozenset
            else:
                elements = None
            if elements is not None:
                subtargets = _cached_get_args(target)
                if not subtargets:
                    values.append(container(elements))
                    break
                tasks.append(("build", cache_key, container, len(elements), None))
                tasks.extend(("decode", element, subtargets[0]) for element in reversed(elements))
                break
            elif issubclass(target_class, tuple) and getattr(target_class, "_fields", None) is None:
                subtargets = _cached_get_args(target)
                if len(subtargets) >= 2 and subtargets[-1] == Ellipsis:
                    subtargets = subtargets[:-1] + tuple(subtargets[-2] for _ in range(len(symbol.arguments) - 1))
                if symbol.name != "" or len(subtargets) > len(symbol.arguments):
                    continue
                fields, child_targets = None, subtargets
            else:
                fields = _get_record_field_targets(target, target_class)
                if _get_record_predicate_name(target_class) != symbol.name or len(fields) != len(symbol.arguments):
                    continue
                fields, child_targets = tuple(fields), tuple(fields.values())
            tasks.append(("build", cache_key, target_class, len(child_targets), fields))
            tasks.extend(
                ("decode", value, child_target)
                for value, child_target in reversed(tuple(zip(symbol.arguments, child_targets)))
            )
            break
        else:
            raise FailedInstantiationExn(f"'{symbol}' is not of type {target_type}")
    return values.pop()


def findInModel(
    model: clingo.Model, target_type: typing.Any = typing.Any, atoms: bool = True, theory: bool = True
) -> dict[clingo.Symbol, typing.Any]:
    """Return model symbols that decode as ``target_type``."""
    result = dict()
    for target in _union_rows(target_type):
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
