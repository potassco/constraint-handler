intToFloatOperator(sqrt;cos;sin;tan;acos;asin;atan).
floatUnOperator(abs;sqrt;cos;sin;tan;acos;asin;atan;minus;floor).
floatBinOperator(add;sub;mult;div;pow;leq;lt;geq;gt).

stageCompute(OP,ARGS,L) :- compute(OP,ARGS), intToFloatOperator(OP), ARGS = (int,(V,())), L=(V,()).
stageCompute(OP,ARGS,L) :- compute(OP,ARGS), floatUnOperator(OP), ARGS=(float,(V,())), L=(V,()).
stageCompute(OP,ARGS,L) :- compute(OP,ARGS), floatBinOperator(OP), ARGS=(T1,(V1,(T2,(V2,())))), L=(V1,(V2,())),
    (T1;T2)=float, T1=(float;int), T2=(float;int).
stagePCompute(OP,S,ARGS) :- compute(OP,ARGS), OP=python(E), eValue(E,str,S).

computed(OP,ARGS,T,RES) :- stageCompute(OP,ARGS,L), (T,RES) = @pythonEvalOperator(OP,L).
computed(OP,ARGS,T,RES) :- stagePCompute(OP,S,ARGS), L=@pythonMergeTypes(ARGS), (T,RES) = @pythonEvalOperator(S,L).

computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=eq,  ARGS = (float,(V1,(float,(V2,())))), V1 =  V2.
computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=neq, ARGS = (float,(V1,(float,(V2,())))), V1 != V2.
computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=eq,  ARGS = (float,(V1,(float,(V2,())))), V1 != V2.
computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=neq, ARGS = (float,(V1,(float,(V2,())))), V1 =  V2.

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
        #print(clFn,clArgs)
        pArgs = myClorm.cltopy(clArgs,list[evaluator.noPredConstant])
        pFn = myClorm.cltopy(clFn,evaluator.noPredOperator)
        pRes = evaluator.evaluate_operator(dict(),pFn,pArgs)
        #prettyArgs = "(" + ", ".join(str(v) for v in pArgs) + ")"
        #print(f"eval operation: {clFn}{prettyArgs}",end=" ")
        #print(pRes)
        pType = evaluator.get_baseType(pRes)
        if pRes is None:
            return []
        if pType is None:
            print("float.lp unsupported type",pRes)
            return []
        return myClorm.pytocl((pType,pRes))
    except Exception as exn:
        print(f"Python error when evaluating {pFn} on {pArgs}: {exn}.")
        return []

def pythonMergeTypes(clArgs):
    pArgs = myClorm.cltopy(clArgs,list)
    skipped = [pArgs[2*i+1] for i in range(int(len(pArgs)/2))]
    return myClorm.pytocl(skipped)

#end.
