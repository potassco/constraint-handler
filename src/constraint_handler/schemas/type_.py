import clingo

import constraint_handler.schemas.warning as warning
import constraint_handler.utils.common as common
import constraint_handler.utils.python_type_model as analysis

BaseType = common.PPEnum(
    "BaseType", ["int", "float", "string", "symbol", "bool", "none", "function", "multimap", "set"]
)

OtherType = common.PPEnum("OtherType", ["bot", "top"])


def ch_type(t: analysis.TypeInfo):
    match t:
        case analysis.Scalar.INT:
            return (BaseType.int, [])
        case analysis.Scalar.BOOL:
            return (BaseType.bool, [])
        case analysis.Scalar.FLOAT:
            return (BaseType.float, [])
        case analysis.Scalar.STRING:
            return (BaseType.string, [])
        case analysis.Scalar.SYMBOL:
            return (BaseType.symbol, [])
        case analysis.Scalar.NONE:
            return (BaseType.none, [])
        case analysis.FunctionType():
            return (BaseType.function, [])
        case analysis.SetOf():
            return (BaseType.set, [])
        case analysis.DictOf():
            return (BaseType.multimap, [])
        case analysis.UnknownType:
            return (OtherType.top, [warning.Type(warning.TypeWarning.untyped)])
        case analysis.UnsupportedType:
            return (OtherType.bot, [warning.Type(warning.TypeWarning.notSupported)])
        case analysis.ListOf():
            return (OtherType.bot, [warning.Type(warning.TypeWarning.notSupported)])
        case _:
            assert False
            return (None, [warning.Type(warning.TypeWarning.notSupported)])


def py_type(t: analysis.TypeInfo):
    match t:
        case BaseType.set:
            return analysis.SetOf(analysis.UnknownType)
        case BaseType.multimap:
            return analysis.DictOf(analysis.UnknownType, analysis.UnknownType)
        case BaseType.bool:
            return analysis.Scalar.BOOL
        case BaseType.int:
            return analysis.Scalar.INT
        case BaseType.float:
            return analysis.Scalar.FLOAT
        case BaseType.string:
            return analysis.Scalar.STRING
        case BaseType.symbol:
            return analysis.Scalar.SYMBOL
        case BaseType.none:
            return analysis.Scalar.NONE
        case BaseType.function:
            return analysis.FunctionType(None, analysis.UnknownType)
        case OtherType.top:
            return analysis.UnknownType
        case OtherType.bot:
            return None
        case _:
            raise NotImplementedError("py_type", t)
