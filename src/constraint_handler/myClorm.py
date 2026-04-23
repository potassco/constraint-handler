import enum
import itertools
import types
import typing

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
        # print("unnest",symb,l)
        if s.type == clingo.SymbolType.Function and s.name == cons and len(s.arguments) == 2:
            l.append(s.arguments[0])
            s = s.arguments[1]
        elif s.type == clingo.SymbolType.Function and s.name == nil and len(s.arguments) == 0:
            # print("unnest return",l)
            return l
        else:
            raise FailedInstantiationExn(f"{symb} is not a list")


class HashableList(list):
    def __hash__(self):
        return hash(tuple(self))


baseTypes = {"bool": bool, "int": int, "float": float, "string": str, "none": type(None)}
# containers = { "set": set, "list": list, "tuple" : tuple }
containers = {"set": set, "list": list}


def _resolve_type_alias(target):
    while isinstance(target, typing.TypeAliasType):
        target = target.__value__
    return target


def _union_rows(target):
    target = _resolve_type_alias(target)
    origin = typing.get_origin(target)
    if origin in (typing.Union, types.UnionType):
        return typing.get_args(target)
    return [target]


def pytocl(v, dtarget=None):
    if dtarget is None:
        dtarget = type(v)
    rows = _union_rows(dtarget)
    for target in rows:
        target = _resolve_type_alias(target)
        runtime_target = typing.get_origin(target) or target
        if runtime_target == typing.Any:
            return v
        elif not isinstance(runtime_target, type):
            pass
        elif not isinstance(v, runtime_target):
            pass
        elif getattr(runtime_target, "pytocl", None):
            return runtime_target.pytocl(v)
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
            name = predicatedefn_default_predicate_name(runtime_target.__name__)
            args = [pytocl(getattr(v, field)) for field in runtime_target._fields]
            return clingo.Function(name, args)
        elif issubclass(runtime_target, tuple):
            return clingo.Function("", [pytocl(e) for e in v])
        else:
            name = getattr(runtime_target, "name", runtime_target.__name__)
            name = predicatedefn_default_predicate_name(name)
            args = typing.get_type_hints(runtime_target)
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


def cltopy(func, dtarget=typing.Any, halt=True):
    dtarget = _resolve_type_alias(dtarget)
    rows = _union_rows(dtarget)
    for target in rows:
        target = _resolve_type_alias(target)
        utarget = typing.get_origin(target) or target  # unsubscripted_target
        try:
            if target == typing.Any:
                if halt:
                    return func
                else:
                    return cltopyNoTarget(func)
            elif getattr(target, "cltopy", None):
                return target.cltopy(func, halt=halt)
            elif getattr(target, "_fields", None) is not None:
                if func.type == clingo.SymbolType.Function:  # NamedTuple
                    assert getattr(target, "__name__", None) is not None
                    name = predicatedefn_default_predicate_name(target.__name__)
                    if isinstance(target, type):
                        assert getattr(target, "_field_defaults", None) is not None
                        targets = typing.get_type_hints(target)
                        targets.update(target._field_defaults)
                    else:
                        targets = target.asdict()
                    if name == func.name and len(target._fields) == len(func.arguments):
                        args = (
                            cltopy(symb, targets.get(field), halt)
                            for symb, field in zip(func.arguments, target._fields)
                        )
                        return target(*args)
            elif any(isinstance(utarget, t) for t in list(baseTypes.values()) + [list, clingo.Symbol]):
                if cltopy(func, halt=halt) == target:
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
                    subtarget = typing.get_args(target)
                    un = unnest(func)
                    result = (
                        [cltopy(e, subtarget[0], halt) for e in un]
                        if subtarget
                        else [cltopyNoTarget(e) for e in un] if not halt else un
                    )
                    return HashableList(result)
                elif issubclass(utarget, set) or issubclass(utarget, frozenset):
                    subtarget = typing.get_args(target)
                    if func.type == clingo.SymbolType.Function and func.name == "set" and len(func.arguments) == 1:
                        un = unnest(func.arguments[0])
                        result = (
                            frozenset(cltopy(e, subtarget[0], halt) for e in un)
                            if subtarget
                            else frozenset(cltopyNoTarget(e) for e in un) if not halt else frozenset(un)
                        )
                        return result
                elif issubclass(utarget, tuple):
                    subtargets = typing.get_args(target)
                    if len(subtargets) >= 2 and subtargets[-1] == Ellipsis and func.type == clingo.SymbolType.Function:
                        subtargets = subtargets[:-1] + tuple(subtargets[-2] for _ in range(len(func.arguments) - 1))
                    if (
                        func.type == clingo.SymbolType.Function
                        and func.name == ""
                        and len(subtargets) <= len(func.arguments)
                    ):
                        zipped = list(itertools.zip_longest(func.arguments, subtargets))
                        result = tuple(cltopy(symb, subt, halt) for (symb, subt) in zipped)
                        return result
            ### Missing is instance of NamedTuple
            ######
            else:
                if func.type == clingo.SymbolType.Function:
                    print(f"helloe func ={func}, target = {target}")
                    print(isinstance(typing.get_origin(target), type))
                    print(issubclass(typing.get_origin(target), list))
                    assert False
                    name = getattr(target, "name", target.__name__)
                    name = predicatedefn_default_predicate_name(name)
                    args = typing.get_type_hints(target).values()
                    # print(f"product function '{len(func.arguments),func.name,func}' with '{len(args),name,args}', match? {name == func.name and len(args) == len(func.arguments)}")
                    if name == func.name and len(args) == len(func.arguments):
                        return target(*(cltopy(symb, field) for symb, field in zip(func.arguments, args)))
            # print(f"ctp conj failure '{func}' is not of type '{target}'")
            raise FailedInstantiationExn(f"'{func}' is not of type '{target}'")
        except FailedInstantiationExn:
            # print(f"disj failed once {func,target} {exn}")
            pass
    raise FailedInstantiationExn(f"'{func}' is not of type {dtarget}")


def findInModel(model, dtarget=typing.Any, atoms=True, theory=True):
    while isinstance(dtarget, typing.TypeAliasType):
        dtarget = dtarget.__value__
    rows = typing.get_args(dtarget) if typing.get_origin(dtarget) in (typing.Union, types.UnionType) else [dtarget]
    result = dict()
    for target in rows:
        # print(f"ctp {target} {type(target)}")
        for symb in model.symbols(atoms=atoms, theory=theory):
            try:
                v = cltopy(symb, target)
                result[symb] = v
            except FailedInstantiationExn:
                pass
    return result


def findInControl(ctl, dtarget=typing.Any):
    while isinstance(dtarget, typing.TypeAliasType):
        dtarget = dtarget.__value__
    rows = typing.get_args(dtarget) if typing.get_origin(dtarget) in (typing.Union, types.UnionType) else [dtarget]
    result = dict()
    for target in rows:
        if target == typing.Any:
            for atom in ctl.symbolic_atoms:
                result[atom] = cltopy(atom.symbol)
        elif getattr(target, "_fields", None) is not None:
            assert getattr(target, "__name__", None) is not None
            name = predicatedefn_default_predicate_name(target.__name__)
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
    while isinstance(dtarget, typing.TypeAliasType):
        dtarget = dtarget.__value__
    rows = typing.get_args(dtarget) if typing.get_origin(dtarget) in (typing.Union, types.UnionType) else [dtarget]
    result = dict()
    for target in rows:
        if getattr(target, "_fields", None) is not None:
            assert getattr(target, "__name__", None) is not None
            name = predicatedefn_default_predicate_name(target.__name__)
            arity = len(target._fields)
            for atom in ctl.symbolic_atoms.by_signature(name, arity):
                try:
                    result[cltopy(atom.symbol, target)] = ctl.solver_literal(atom.literal)
                except FailedInstantiationExn:
                    pass
        else:
            raise ValueError("findInControl: not sure what to do with target", target)
    return result
