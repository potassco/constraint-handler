eValue(E,T,V) :- expression(E), E=variable(VAR), compileAssign(NAME,VAR,E2), eValue(E2,T,V).

floatOperator(abs;sqrt;cos;sin;acos;asin;add;mult;div;eq;neq;leq;lt;geq;gt;minus).
operataorValue(OE,OE) :- expression(E), E=operation(OE, EL), floatOperator(OE).
operataorValue(OE,S)  :- expression(E), E=operation(OE, EL), OE=python(EXP), eValue(EXP,str,S).
eValue(E,T,RES) :- stagePythonCall(E,P,L), (T,RES) = @pythonEvalOperator(P,L).
stagePythonCall(E,OP,L) :- expression(E), E=operation(OE, (E1,())),
    operataorValue(OE,OP),
    eValue(E1,T1,V1),
    L = (V1,()),
    #false : T1!=float.

stagePythonCall(E,OP,L) :- expression(E), E=operation(OE, (E1,(E2,()))),
    operataorValue(OE,OP),
    eValue(E1,T1,V1), eValue(E2,T2,V2),
    L = (V1,(V2,())),
    #false : T1!=float, T2!=float.

#script(python)

import constraint_handler.myClorm
import operator
import clingo
import constraint_handler.evaluator as evaluator

def getFn(clFn):
    #cFn = myClorm.cltopy(clFn,evaluator.noPredOperator)
    #print(cFn)
    cFn = myClorm.cltopy(clFn)
    pFn = None
    if cFn.type == clingo.SymbolType.String:
        pFn = eval(cFn.str)
    elif cFn.type == clingo.SymbolType.Function and cFn.name == "str":
        pFn = eval(cFn.arguments[0].str)
    else:
        print(f"python call isn't a str {cFn}")
    return pFn


pairList = list[tuple[evaluator.BaseType,evaluator.noPredConstant]]

def pythonEvalOperator(clFn,clArgs):
    try:
        pArgs = myClorm.cltopy(clArgs,list[evaluator.noPredConstant])
        #print("pArgs2",pArgs)
        #pFn = getFn(clFn)
        pFn = myClorm.cltopy(clFn,evaluator.noPredOperator)
        #print(pFn,pArgs,type(pArgs[0]))
        prettyArgs = "(" + ", ".join(str(v) for v in pArgs) + ")"
        print(f"eval operation: {clFn}{prettyArgs}",end=" ")
        pRes = evaluator.evaluate_operator(dict(),pFn,pArgs)
        print(pRes)
        #pRes = pFn(*pArgs)
        st = evaluator.toPair(pRes)
        return myClorm.pytocl(st)
    except Exception as exn:
        print(f"Python error when evaluating {pFn} on {pArgs}: {exn}.")
        return []

#end.
