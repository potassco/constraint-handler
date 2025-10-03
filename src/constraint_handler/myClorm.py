import collections
import enum
import itertools
import types
import typing

import clorm
import clorm.clingo as clingo
import clorm.orm.core


def predicatedefn_default_predicate_name(name):
    return clorm.orm.core._predicatedefn_default_predicate_name(name) if name else ""


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
            return None


# def Tuple(subtype):
def Function(name, args=None):  # ,key=0):
    args = [] if args is None else args
    field_names = ["" for i in args]
    return collections.namedtuple(name, field_names, defaults=args, rename=True)


def Tuple(name="", args=None, default=None):
    # fields = args if args is not None
    class Wrapper(tuple):  # collections.namedtuple(name,field_names,defaults=dargs,rename=True)):
        __name__ = name
        _default = default

        def __new__(cls, *dargs):
            return super().__new__(cls, dargs)

    return Wrapper


baseTypes = {"bool": bool, "int": int, "float": float, "str": str, "none" : type(None) }
# containers = { "set": set, "list": list, "tuple" : tuple }
containers = {"set": set, "list": list}


def pytocl(v, dtarget=None):
    if dtarget is None:
        dtarget = type(v)
    # print(f"hello ptc disj trying '{v}' with rows '{dtarget}'")
    # print(f"the type is {type(v)}")
    # if dtarget != typing.Any and not isinstance(v,dtarget):
    #    print(f"hello ptc disj failed '{v}' with rows '{dtarget}'")
    #    raise TypeError(f"'{v}' is not of type '{dtarget}'")
    rows = typing.get_args(dtarget) if dtarget != typing.Any and isinstance(dtarget, types.UnionType) else [dtarget]
    # print(f"ptc disj trying '{v}' with rows '{rows}'")
    for target in rows:
        # print(f"ptc {type(target)}")
        if target == typing.Any:
            return v
        elif not isinstance(v, target):
            pass
        elif issubclass(target, clorm.Predicate):
            return target._field.pytocl(v)
        elif getattr(target, "pytocl", None):
            return target.pytocl(v)
        elif issubclass(target, clorm.Raw):
            return v.symbol
        elif issubclass(target, clingo.Symbol):
            return v
        elif issubclass(target, enum.Enum):
            if isinstance(v, target):
                return clingo.Function(predicatedefn_default_predicate_name(v.name), [])
        elif target == types.NoneType:
            return clingo.Function("none", [])
        elif issubclass(target, bool):
            return clingo.Function("true" if v else "false", [])
        elif issubclass(target, int):
            return clingo.Number(v)
        elif issubclass(target, str):
            return clingo.String(v)
        elif issubclass(target, float):
            return clingo.Function("float", [clingo.String(str(v))])
        elif issubclass(target, list):
            return nest([pytocl(e) for e in v])
        elif issubclass(target, set) or issubclass(target, frozenset):
            return clingo.Function("set", [nest([pytocl(e) for e in v])])
        elif any(issubclass(target, cls) for cls in containers.values()):
            assert False
            n = next(name for name, cls in containers.items() if issubclass(target, cls))
            return clingo.Function(n, [nest([pytocl(e) for e in v])])
        elif getattr(target, "_fields", None) is not None:
            assert getattr(target, "__name__", None) is not None
            name = predicatedefn_default_predicate_name(target.__name__)
            args = [pytocl(getattr(v, field)) for field in target._fields]
            return clingo.Function(name, args)
        elif issubclass(target, tuple):
            return clingo.Function("", [pytocl(e) for e in v])
        else:
            print("myclorm pytocl", v, target)
            name = getattr(target, "name", target.__name__)
            name = predicatedefn_default_predicate_name(name)
            args = typing.get_type_hints(target)
            # print(name,args)
            return clingo.Function(name, [pytocl(getattr(v, name), field) for name, field in args.items()])
    # print(f"ptc disj failed all {v,dtarget}")
    raise TypeError(f"'{v}' is not of type {dtarget}")


def cltopyNoTarget(func):
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
    elif func.name == "set" and len(func.arguments) == 1 and unnest(func.arguments[0]) is not None:
        return frozenset(cltopyNoTarget(e) for e in unnest(func.arguments[0]))
    elif unnest(func) is not None:
        # print("hella",func,list(unnest(func)))
        return [cltopyNoTarget(e) for e in unnest(func)]
    elif func.name == "":
        return tuple([cltopyNoTarget(e) for e in func.arguments])
    #    elif func.name in containers and len(func.arguments) == 1:
    #        l = unnest(func.arguments[0])
    #        if l is not None:
    #            return containers[func.name]([cltopyNoTarget(e) for e in l])
    else:
        return func


def cltopy(func, dtarget=typing.Any):
    rows = typing.get_args(dtarget) if typing.get_origin(dtarget) in (typing.Union, types.UnionType) else [dtarget]
    # print(f"ctp disj trying '{func}' with rows '{rows}'")
    for target in rows:
        # print(f"ctp {target} {type(target)}")
        utarget = typing.get_origin(target) or target  # unsubscripted_target
        try:
            if target == typing.Any:
                return cltopyNoTarget(func)
            elif getattr(target, "cltopy", None):
                return target.cltopy(func)
            elif getattr(target, "_fields", None) is not None:
                # print(f"myclorm fields {func},{target}")
                if func.type == clingo.SymbolType.Function:  # NamedTuple
                    assert getattr(target, "__name__", None) is not None
                    name = predicatedefn_default_predicate_name(target.__name__)
                    if isinstance(target, type):
                        assert getattr(target, "_field_defaults", None) is not None
                        targets = typing.get_type_hints(target)
                        targets.update(target._field_defaults)
                    else:
                        targets = target.asdict()
                    # print("hel",func,targets)
                    if name == func.name and len(target._fields) == len(func.arguments):
                        args = (cltopy(symb, targets.get(field)) for symb, field in zip(func.arguments, target._fields))
                        # print("returns",func,targets,args,[(symb,targets.get(field)) for symb,field in zip(func.arguments,fields)])
                        return target(*args)
            # elif any(isinstance(target,t) for t in [bool,int,str,float,list,clingo.Symbol]): # + list(containers.values())):
            elif any(
                isinstance(utarget, t) for t in list(baseTypes.values()) + [list, clingo.Symbol]
            ):  # + list(containers.values())):
                if cltopy(func) == target:
                    return target
            elif isinstance(utarget, type):
                # print(f"myclorm type {func},{target},{typing.get_origin(target)}")
                if issubclass(utarget, clingo.Symbol):
                    return func
                elif issubclass(utarget, enum.Enum):
                    if func.type == clingo.SymbolType.Function and len(func.arguments) == 0 and func.name in target:
                        return target(func.name)
                # TODO: make it work with ints as well?
                elif any(issubclass(utarget, t) for t in list(baseTypes.values())):
                    value = cltopy(func)
                    if value != func and isinstance(value, utarget):
                        return value
                elif issubclass(utarget, list):
                    subtarget = typing.get_args(target)
                    # print("subt",target,subtarget)
                    # return [cltopy(e,subtarget[0]) for e in unnest(func)] if subtarget else [cltopyNoTarget(e) for e in unnest(func)]
                    un = unnest(func)
                    result = [cltopy(e, subtarget[0]) for e in un] if subtarget else [cltopyNoTarget(e) for e in un]
                    return result
                elif issubclass(utarget, tuple):
                    # print(f"myclorm tuple {func},{target}")
                    subtargets = typing.get_args(target)
                    if (
                        func.type == clingo.SymbolType.Function
                        and func.name == ""
                        and len(subtargets) <= len(func.arguments)
                    ):
                        # print(f"myclorm tuple {func},{target}")
                        zipped = list(itertools.zip_longest(func.arguments, subtargets))
                        result = tuple(cltopy(symb, subt) for (symb, subt) in zipped)
                        # print(f"tuple result {result} {func} {getattr(target,'_default',None)}")
                        return result
                    return clorm.Raw(func)
            ### Missing is instance of NamedTuple
            ######
            # elif issubclass(target,int):
            #    if func.type == clingo.SymbolType.Number:
            #       return target(func.number)
            # elif issubclass(target,str):
            #    if func.type == clingo.SymbolType.String:
            #       return target(func.string)
            # elif issubclass(target,float):
            #    if func.type == clingo.SymbolType.Function and func.name == "float" and len(func.arguments) == 1:
            #       arg = func.arguments[0]
            #       if arg.type == clingo.SymbolType.String:
            #          return target(arg.string)
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
            raise TypeError(f"'{func}' is not of type '{target}'")
        except (ValueError, TypeError):
            # except TypeError as exn:
            # print(f"disj failed once {func,target} {exn}")
            pass
        except Exception as exn:
            print("hello", exn)
            print(exn)
            raise exn
    # print(f"ctp disj failed all {func,dtarget}")
    raise TypeError(f"'{func}' is not of type {dtarget}")


def define_adt_field(
    entry,
    *,
    name: str = "",
) -> typing.Type[clorm.BaseField]:

    subclass_name = name if name else "AnonymousADTField"

    # Support function - to check input values

    newclass = type(subclass_name, (clorm.BaseField,), {"pytocl": pytocl, "cltopy": lambda func: cltopy(func, entry)})
    return newclass
