import builtins

import constraint_handler.schemas.warning as warning
import constraint_handler.utils.common as common
import constraint_handler.utils.python_type_model as analysis

BaseType = common.PPEnum(
    "BaseType", ["int", "float", "string", "symbol", "bool", "none", "function", "multimap", "set"]
)


def ch_type(t: analysis.TypeInfo):
    match t:
        case analysis.ScalarType(typ=builtins.int):
            return (BaseType.int, [])
        case analysis.ScalarType(typ=builtins.bool):
            return (BaseType.bool, [])
        case analysis.ScalarType(typ=builtins.float):
            return (BaseType.float, [])
        case analysis.ScalarType(typ=builtins.str):
            return (BaseType.string, [])
        case analysis.ScalarType(typ=clingo.Symbol):
            return (BaseType.symbol, [])
        case analysis.ScalarType(typ=types.NoneType):
            return (BaseType.none, [])
        case analysis.FunctionType():
            return (BaseType.function, [])
        case analysis.SetOf():
            return (BaseType.set, [])
        case analysis.DictOf():
            return (BaseType.multimap, [])
        case analysis.UnknownType:
            return (None, [warning.Type(warning.TypeWarning.notSupported)])
        case _:
            return (None, [warning.Type(warning.TypeWarning.notImplemented)])


def py_type(t: analysis.TypeInfo):
    match t:
        case BaseType.set:
            return analysis.SetOf(analysis.ScalarType(analysis.UnknownType))
        case BaseType.multimap:
            return analysis.DictOf(analysis.ScalarType(analysis.UnknownType), analysis.ScalarType(analysis.UnknownType))
        case BaseType.bool:
            return analysis.ScalarType(bool)
        case BaseType.int:
            print("returning", analysis.ScalarType(int))
            return analysis.ScalarType(int)
        case BaseType.float:
            return analysis.ScalarType(float)
        case BaseType.string:
            return analysis.ScalarType(str)
        case BaseType.symbol:
            return analysis.ScalarType(clingo.Symbol)
        case BaseType.none:
            return analysis.ScalarType(type(None))
        case BaseType.function:
            return analysis.FunctionType(None, frozenset((analysis.UnknownType,)))
        case _:
            raise NotImplementedError("py_type", t)
