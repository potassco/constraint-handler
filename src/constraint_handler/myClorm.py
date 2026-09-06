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
containers = {"set": set, "list": list}
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


@cache
def _get_record_predicate_name(target):
    return predicatedefn_default_predicate_name(target.__name__)


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


def pytocl(v, dtarget=None):
    if dtarget is None:
        dtarget = type(v)

    if dtarget is int:
        return clingo.Number(v)
    if dtarget is bool:
        return clingo.Function("true" if v else "false", [])
    if dtarget is str:
        return clingo.String(v)
    if dtarget is float:
        return clingo.Function("float", [clingo.String(str(v))])
    if dtarget is types.NoneType or dtarget is type(None):
        return clingo.Function("none", [])
    if dtarget is list:
        return nest([pytocl(e) for e in v])
    if dtarget is tuple:
        return clingo.Function("", [pytocl(e) for e in v])
    if dtarget is set or dtarget is frozenset:
        return clingo.Function("set", [nest(sorted([pytocl(e) for e in v]))])
    if dtarget is clingo.Symbol:
        return v

    rows = _union_rows(dtarget)
    for target in rows:
        target = _resolve_type_alias(target)
        runtime_target = _cached_get_origin(target) or target
        custom_value = _resolve_custom_converter(target, "pytocl", v)
        if custom_value is not _NO_CUSTOM_CONVERTER:
            return custom_value
        if runtime_target == typing.Any:
            return v
        elif not isinstance(runtime_target, type):
            pass
        elif not isinstance(v, runtime_target):
            pass
        elif issubclass(runtime_target, clingo.Symbol):
            return v
        elif issubclass(runtime_target, enum.Enum):
            symbol_name = v.value if isinstance(v.value, str) else predicatedefn_default_predicate_name(v.name)
            return clingo.Function(symbol_name, [])
        elif runtime_target == types.NoneType:
            return clingo.Function("none", [])
        elif issubclass(runtime_target, bool):
            return clingo.Function("true" if v else "false", [])
        elif issubclass(runtime_target, int):
            return clingo.Number(v)
        elif issubclass(runtime_target, str):
            return clingo.String(v)
        elif issubclass(runtime_target, float):
            return clingo.Function("float", [clingo.String(str(v))])
        elif issubclass(runtime_target, list):
            return nest([pytocl(e) for e in v])
        elif issubclass(runtime_target, set) or issubclass(runtime_target, frozenset):
            return clingo.Function("set", [nest(sorted([pytocl(e) for e in v]))])
        elif dataclasses.is_dataclass(runtime_target):
            name = _get_record_predicate_name(runtime_target)
            fields = (field for field in dataclasses.fields(runtime_target) if field.init)
            return clingo.Function(name, [pytocl(getattr(v, field.name)) for field in fields])
        elif getattr(runtime_target, "_fields", None) is not None:
            assert getattr(runtime_target, "__name__", None) is not None
            name = _get_record_predicate_name(runtime_target)
            args = [pytocl(getattr(v, field)) for field in runtime_target._fields]
            return clingo.Function(name, args)
        elif issubclass(runtime_target, tuple):
            return clingo.Function("", [pytocl(e) for e in v])
        else:
            name = _get_record_predicate_name(runtime_target)
            args = _cached_get_type_hints(runtime_target)
            return clingo.Function(name, [pytocl(getattr(v, name), field) for name, field in args.items()])
    raise FailedInstantiationExn(f"'{v}' is not of type {dtarget}")


def cltopyNoTarget(func):
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
def cltopy(func, dtarget=typing.Any):
    dtarget = _resolve_type_alias(dtarget)
    rows = _union_rows(dtarget)
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
                    fields = tuple(field for field in dataclasses.fields(target_class) if field.init)
                    targets = _cached_get_type_hints(target_class)
                    typevars = dict(zip(getattr(target_class, "__parameters__", ()), _cached_get_args(target)))
                    if name == func.name and len(fields) == len(func.arguments):
                        args = {
                            field.name: cltopy(
                                symb, typevars.get(targets.get(field.name), targets.get(field.name, typing.Any))
                            )
                            for symb, field in zip(func.arguments, fields)
                        }
                        try:
                            return target_class(**args)
                        except TypeError as error:
                            raise FailedInstantiationExn(str(error)) from error
            elif getattr(target_class, "_fields", None) is not None:
                if func.type == clingo.SymbolType.Function:  # NamedTuple
                    name = _get_record_predicate_name(target_class)
                    targets = _cached_get_type_hints(target_class)
                    typevars = dict(zip(getattr(target_class, "__parameters__", ()), _cached_get_args(target)))
                    if name == func.name and len(target_class._fields) == len(func.arguments):
                        args = (
                            cltopy(symb, typevars.get(targets.get(field), targets.get(field, typing.Any)))
                            for symb, field in zip(func.arguments, target_class._fields)
                        )
                        return target_class(*args)
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
                    un = unnest(func)
                    if subtarget:
                        result = [cltopy(e, subtarget[0]) for e in un]
                    else:
                        result = un
                    return ImmutableList(result)
                elif issubclass(target_class, set) or issubclass(target_class, frozenset):
                    subtarget = _cached_get_args(target)
                    if func.type == clingo.SymbolType.Function and func.name == "set" and len(func.arguments) == 1:
                        un = unnest(func.arguments[0])
                        if subtarget:
                            result = frozenset(cltopy(e, subtarget[0]) for e in un)
                        else:
                            result = frozenset(un)
                        return result
                elif issubclass(target_class, tuple):
                    subtargets = _cached_get_args(target)
                    if len(subtargets) >= 2 and subtargets[-1] == Ellipsis and func.type == clingo.SymbolType.Function:
                        subtargets = subtargets[:-1] + tuple(subtargets[-2] for _ in range(len(func.arguments) - 1))
                    if (
                        func.type == clingo.SymbolType.Function
                        and func.name == ""
                        and len(subtargets) <= len(func.arguments)
                    ):
                        zipped = list(itertools.zip_longest(func.arguments, subtargets))
                        result = tuple(cltopy(symb, subt) for (symb, subt) in zipped)
                        return result
                elif func.type == clingo.SymbolType.Function:
                    name = _get_record_predicate_name(target_class)
                    args = _cached_get_type_hints(target_class).values()
                    if name == func.name and len(args) == len(func.arguments):
                        return target_class(*(cltopy(symb, field) for symb, field in zip(func.arguments, args)))
            raise FailedInstantiationExn(f"'{func}' is not of type '{target}'")
        except FailedInstantiationExn:
            pass
    raise FailedInstantiationExn(f"'{func}' is not of type {dtarget}")


def findInModel(model, dtarget=typing.Any, atoms=True, theory=True):
    rows = _union_rows(dtarget)
    result = dict()
    for target in rows:
        for symb in model.symbols(atoms=atoms, theory=theory):
            try:
                v = cltopy(symb, target)
                result[symb] = v
            except FailedInstantiationExn:
                pass
    return result


def findInControl(ctl, dtarget=typing.Any):
    rows = _union_rows(dtarget)
    result = dict()
    for target in rows:
        target_class = _cached_get_origin(target) or target
        if target == typing.Any:
            for atom in ctl.symbolic_atoms:
                result[atom] = cltopy(atom.symbol)
        elif dataclasses.is_dataclass(target_class):
            name = _get_record_predicate_name(target_class)
            arity = sum(field.init for field in dataclasses.fields(target_class))
            for atom in ctl.symbolic_atoms.by_signature(name, arity):
                try:
                    result[atom] = cltopy(atom.symbol, target)
                except FailedInstantiationExn:
                    pass
        elif getattr(target_class, "_fields", None) is not None:
            name = _get_record_predicate_name(target_class)
            arity = len(target_class._fields)
            for atom in ctl.symbolic_atoms.by_signature(name, arity):
                try:
                    result[atom] = cltopy(atom.symbol, target)
                except FailedInstantiationExn:
                    pass
        else:
            raise ValueError("findInControl: not sure what to do with target", target)
    return result


def findInPropagateInit(ctl, dtarget):
    rows = _union_rows(dtarget)
    result = dict()
    for target in rows:
        target_class = _cached_get_origin(target) or target
        if dataclasses.is_dataclass(target_class):
            name = _get_record_predicate_name(target_class)
            arity = sum(field.init for field in dataclasses.fields(target_class))
            for atom in ctl.symbolic_atoms.by_signature(name, arity):
                try:
                    if ctl.solver_literal(atom.literal) == -1:
                        continue
                    result[cltopy(atom.symbol, target)] = ctl.solver_literal(atom.literal)
                except FailedInstantiationExn:
                    pass
        elif getattr(target_class, "_fields", None) is not None:
            name = _get_record_predicate_name(target_class)
            arity = len(target_class._fields)
            for atom in ctl.symbolic_atoms.by_signature(name, arity):
                try:
                    if ctl.solver_literal(atom.literal) == -1:
                        continue
                    result[cltopy(atom.symbol, target)] = ctl.solver_literal(atom.literal)
                except FailedInstantiationExn:
                    pass
        else:
            raise ValueError("findInControl: not sure what to do with target", target)
    return result
