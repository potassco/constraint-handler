#script(python)
import itertools
import operator
import typing
from collections import defaultdict
from functools import cache
import math

import clingo

import constraint_handler.myClorm as myClorm
import constraint_handler.evaluator as evaluator
import constraint_handler.schemas.atom as atom
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.statement as statement
import constraint_handler.schemas.type_ as type_
import constraint_handler.schemas.warning as warning
import constraint_handler.solver_environment as solver_environment
import constraint_handler.utils.python_statement_analysis as python_analysis


@cache
def pythonListElements(clL):
    try:
        return myClorm.cltopy(clL,list[clingo.Symbol])
    except myClorm.FailedInstantiationExn:
        return []

@cache
def pythonReversedList(clL):
    pL = pythonListElements(clL)
    return myClorm.pytocl(list(reversed(pL)))

@cache
def pythonEnumerateElements(clL):
    pL = pythonListElements(clL)
    return [myClorm.pytocl(e) for e in enumerate(pL)]

@cache
def pythonListLength(clL):
    pL = pythonListElements(clL)
    return myClorm.pytocl(len(pL))

@cache
def pythonIsList(clL):
    try:
        myClorm.cltopy(clL,list)
        return myClorm.pytocl(True)
    except myClorm.FailedInstantiationExn:
        return myClorm.pytocl(False)

@cache
def pythonIsString(clS):
    return myClorm.pytocl(clS.type == clingo.SymbolType.String)

@cache
def pythonIsTuple(clT):
    return myClorm.pytocl(clT.type == clingo.SymbolType.Function and clT.name == "" and (len(clT.arguments) != 2 or clT.arguments[1] != clingo.Function("")))

@cache
def pythonScaleInteger(value, scale):
    """
    Scales the given float/bool/integer value by the provided scale factor.
    Returns floor of scaled value
    """
    return myClorm.pytocl(math.floor(myClorm.cltopy(value, expression.constant) * myClorm.cltopy(scale, expression.constant)))

@cache
def _to_val(type_, v):
        return clingo.Function("val", [clingo.Function(type_, []), myClorm.pytocl(v)])

@cache
def pythonFloatUnary(operator, val):
    value = float(val.arguments[0].string)
    match operator.name:
        case "abs":
            return _to_val("float", abs(value))
        case "ceil":
            return _to_val("int", math.ceil(value))
        case "floor":
            return _to_val("int", math.floor(value))
        case "minus":
            return _to_val("float", -value)
        case _:
            return clingo.Function("bad", [])

@cache
def pythonFloatBinary(operator, val1, val2):
    """ given an operator and two values, evaluates the result of applying the operator to the values as floating string ("42.0") """
    if val1.type == clingo.SymbolType.Number:
        value1 = val1.number
    elif val1.type == clingo.SymbolType.Function and \
         val1.name == "float" and len(val1.arguments) == 1 and \
         val1.arguments[0].type == clingo.SymbolType.String:
        value1 = float(val1.arguments[0].string)

    if val2.type == clingo.SymbolType.Number:
        value2 = val2.number
    elif val2.type == clingo.SymbolType.Function and \
         val2.name == "float" and len(val2.arguments) == 1 and \
         val2.arguments[0].type == clingo.SymbolType.String:
        value2 = float(val2.arguments[0].string)



    match operator.name:
        case "add":
            return _to_val("float", value1 + value2)
        case "mult":
            return _to_val("float", value1 * value2)
        case "int_div":
            if value2 == 0.0:
                return clingo.Function("bad", [])
            return _to_val("int", math.floor(value1 / value2))
        case "float_div":
            if value2 == 0.0:
                return clingo.Function("bad", [])
            return _to_val("float", value1 / value2)
        case "sub":
            return _to_val("float", value1 - value2)
        case "pow":
            return _to_val("float", value1 ** value2)
        case "eq":
            return _to_val("bool", value1 == value2)
        case "neq":
            return _to_val("bool", value1 != value2)
        case "leq":
            return _to_val("bool", value1 <= value2)
        case "lt":
            return _to_val("bool", value1 < value2)
        case "geq":
            return _to_val("bool", value1 >= value2)
        case "gt":
            return _to_val("bool", value1 > value2)
        case "max":
            return _to_val("float", max(value1, value2))
        case "min":
            return _to_val("float", min(value1, value2))
        case _:
            return clingo.Function("bad", [])



@cache
def pythonTupleElements(clT):
    if clT.type == clingo.SymbolType.Function and clT.name == "":
        return clT.arguments
    else:
        return []
@cache
def pythonStringLength(clStr):
    pStr = myClorm.cltopy(clStr,str)
    return myClorm.pytocl(len(pStr))

@cache
def pythonStringAdd(clStr1,clStr2):
    pStr1 = myClorm.cltopy(clStr1,str)
    pStr2 = myClorm.cltopy(clStr2,str)
    return myClorm.pytocl(pStr1+pStr2)

@cache
def pythonScopeToString(clS,clVar):
    try:
        l = myClorm.cltopy(clS,list)
        prg = str(l[-1])
        var = str(clVar)
        uid = "".join(str(a) for a in reversed(l[:-1]))
        name = f"{prg}_{var}_{uid}"
        return myClorm.pytocl(name)
    except myClorm.FailedInstantiationExn:
        return clS
        #return myClorm.pytocl(False)

@cache
def pythonReify(term):
    if term.type == clingo.SymbolType.Function:
        symb = clingo.symbol.Function(term.name)
        n = len(term.arguments)
        return myClorm.pytocl((clingo.symbol.Function("function"),symb,n,term.arguments))
    elif term.type == clingo.SymbolType.Number:
        return myClorm.pytocl((clingo.symbol.Function("number"),term,0,()))
    else:
        return myClorm.pytocl((clingo.symbol.Function("string"),term,0,()))

@cache
def pythonReflect(kind,term,args):
    if kind == clingo.symbol.Function("function") and term.type == clingo.SymbolType.Function:
        name = term.name
        arguments = myClorm.cltopy(args,list)
        return clingo.Function(name,arguments)
    elif kind == clingo.symbol.Function("number"):
        return term
    elif kind == clingo.symbol.Function("string"):
        return term
    else:
        return []

@cache
def pythonNestedToTuple(values):
    pValues = myClorm.cltopy(values,list)
    return myClorm.pytocl(tuple(pValues))

#end.
