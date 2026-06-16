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


class HashableList(tuple):
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
def _cached_get_namedtuple_targets(target):
    targets = dict(_cached_get_type_hints(target))
    defaults = getattr(target, "_field_defaults", None)
    if defaults is not None:
        targets.update(defaults)
    return targets


@cache
def _get_namedtuple_predicate_name(target):
    return predicatedefn_default_predicate_name(target.__name__)


@cache
def _get_custom_class_predicate_name(target):
    name = getattr(target, "name", None)
    if not isinstance(name, str):
        name = getattr(target, "__name__", None)
    return predicatedefn_default_predicate_name(name)


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
        return clingo.Function("set", [nest([pytocl(e) for e in v])])
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
            return clingo.Function("set", [nest([pytocl(e) for e in v])])
        elif any(issubclass(runtime_target, cls) for cls in containers.values()):
            assert False
            n = next(name for name, cls in containers.items() if issubclass(runtime_target, cls))
            return clingo.Function(n, [nest([pytocl(e) for e in v])])
        elif getattr(runtime_target, "_fields", None) is not None:
            assert getattr(runtime_target, "__name__", None) is not None
            name = _get_namedtuple_predicate_name(runtime_target)
            args = [pytocl(getattr(v, field)) for field in runtime_target._fields]
            return clingo.Function(name, args)
        elif issubclass(runtime_target, tuple):
            return clingo.Function("", [pytocl(e) for e in v])
        else:
            name = _get_custom_class_predicate_name(runtime_target)
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
                return HashableList([cltopyNoTarget(e) for e in l])
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
        utarget = _cached_get_origin(target) or target  # unsubscripted_target
        try:
            if target == typing.Any:
                return func
            custom_value = _resolve_custom_converter(target, "cltopy", func)
            if custom_value is not _NO_CUSTOM_CONVERTER:
                return custom_value
            elif getattr(target, "_fields", None) is not None:
                if func.type == clingo.SymbolType.Function:  # NamedTuple
                    assert getattr(target, "__name__", None) is not None
                    name = _get_namedtuple_predicate_name(target)
                    if isinstance(target, type):
                        assert getattr(target, "_field_defaults", None) is not None
                        targets = _cached_get_namedtuple_targets(target)
                    else:
                        targets = target.asdict()
                    if name == func.name and len(target._fields) == len(func.arguments):
                        args = (cltopy(symb, targets.get(field)) for symb, field in zip(func.arguments, target._fields))
                        return target(*args)
            elif any(isinstance(utarget, t) for t in list(baseTypes.values()) + [list, clingo.Symbol]):
                if cltopy(func) == target:
                    return target
            elif isinstance(utarget, type):
                if issubclass(utarget, clingo.Symbol):
                    return func
                elif issubclass(utarget, enum.Enum):
                    if func.type == clingo.SymbolType.Function and len(func.arguments) == 0:
                        for member in utarget:
                            if (
                                member.name == func.name
                                or predicatedefn_default_predicate_name(member.name) == func.name
                            ):
                                return member
                            if isinstance(member.value, str) and member.value == func.name:
                                return member
                elif issubclass(utarget, bool):
                    if (
                        func.type == clingo.SymbolType.Function
                        and func.name in ["true", "false"]
                        and len(func.arguments) == 0
                    ):
                        return func.name == "true"
                elif issubclass(utarget, int):
                    if func.type == clingo.SymbolType.Number:
                        return func.number
                elif issubclass(utarget, str):
                    if func.type == clingo.SymbolType.String:
                        return func.string
                elif issubclass(utarget, float):
                    if (
                        func.type == clingo.SymbolType.Function
                        and func.name == "float"
                        and len(func.arguments) == 1
                        and func.arguments[0].type in [clingo.SymbolType.String, clingo.SymbolType.Number]
                    ):
                        arg = func.arguments[0]
                        return float(arg.string if arg.type == clingo.SymbolType.String else arg.number)
                elif issubclass(utarget, type(None)):
                    if func.name == "none" and len(func.arguments) == 0:
                        return None
                elif issubclass(utarget, list):
                    subtarget = _cached_get_args(target)
                    un = unnest(func)
                    if subtarget:
                        result = [cltopy(e, subtarget[0]) for e in un]
                    else:
                        result = un
                    return HashableList(result)
                elif issubclass(utarget, set) or issubclass(utarget, frozenset):
                    subtarget = _cached_get_args(target)
                    if func.type == clingo.SymbolType.Function and func.name == "set" and len(func.arguments) == 1:
                        un = unnest(func.arguments[0])
                        if subtarget:
                            result = frozenset(cltopy(e, subtarget[0]) for e in un)
                        else:
                            result = frozenset(un)
                        return result
                elif issubclass(utarget, tuple):
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
            else:
                if func.type == clingo.SymbolType.Function:
                    print(f"helloe func ={func}, target = {target}")
                    print(isinstance(_cached_get_origin(target), type))
                    print(issubclass(_cached_get_origin(target), list))
                    assert False
                    name = getattr(target, "name", target.__name__)
                    name = predicatedefn_default_predicate_name(name)
                    args = _cached_get_type_hints(target).values()
                    if name == func.name and len(args) == len(func.arguments):
                        return target(*(cltopy(symb, field) for symb, field in zip(func.arguments, args)))
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
        if target == typing.Any:
            for atom in ctl.symbolic_atoms:
                result[atom] = cltopy(atom.symbol)
        elif getattr(target, "_fields", None) is not None:
            assert getattr(target, "__name__", None) is not None
            name = _get_namedtuple_predicate_name(target)
            arity = len(target._fields)
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
        if getattr(target, "_fields", None) is not None:
            assert getattr(target, "__name__", None) is not None
            name = _get_namedtuple_predicate_name(target)
            arity = len(target._fields)
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
