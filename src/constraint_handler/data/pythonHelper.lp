#script(python)

import itertools
import operator
import typing

from collections import defaultdict

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


def pythonListElements(clL):
    try:
        return myClorm.cltopy(clL,list[clingo.Symbol])
    except myClorm.FailedInstantiationExn:
        return []

def pythonReversedList(clL):
    pL = pythonListElements(clL)
    return myClorm.pytocl(list(reversed(pL)))

def pythonEnumerateElements(clL):
    pL = pythonListElements(clL)
    return [myClorm.pytocl(e) for e in enumerate(pL)]

def pythonListLength(clL):
    pL = pythonListElements(clL)
    return myClorm.pytocl(len(pL))


def pythonIsList(clL):
    try:
        myClorm.cltopy(clL,list)
        return myClorm.pytocl(True)
    except myClorm.FailedInstantiationExn:
        return myClorm.pytocl(False)

def pythonIsString(clS):
    return myClorm.pytocl(clS.type == clingo.SymbolType.String)

def pythonIsTuple(clT):
    return myClorm.pytocl(clT.type == clingo.SymbolType.Function and clT.name == "" and (len(clT.arguments) != 2 or clT.arguments[1] != clingo.Function("")))

def pythonTupleElements(clT):
    if clT.type == clingo.SymbolType.Function and clT.name == "":
        return clT.arguments
    else:
        return []

def pythonStringLength(clStr):
    pStr = myClorm.cltopy(clStr,str)
    return myClorm.pytocl(len(pStr))

def pythonStringAdd(clStr1,clStr2):
    pStr1 = myClorm.cltopy(clStr1,str)
    pStr2 = myClorm.cltopy(clStr2,str)
    return myClorm.pytocl(pStr1+pStr2)


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

def pythonReify(term):
    if term.type == clingo.SymbolType.Function:
        symb = clingo.symbol.Function(term.name)
        n = len(term.arguments)
        return myClorm.pytocl((clingo.symbol.Function("function"),symb,n,term.arguments))
    elif term.type == clingo.SymbolType.Number:
        return myClorm.pytocl((clingo.symbol.Function("number"),term,0,()))
    else:
        return myClorm.pytocl((clingo.symbol.Function("string"),term,0,()))

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

#end.
