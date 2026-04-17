%%%%%%%%%%%%%%%%% eq neq
_type_extensionalEquality(string).

%%%%%%%%%%%%%%%%% length concat
operator_declare(length,(string,()),int).
operator_declare(concat,(string,(string,())),string).
_computedIdx(E,val(int,N)) :- _computeIdx(E,length), _computeIdx(E,0,val(string,S)), N=@pythonStringLength(S).
_computedIdx(E,val(string,R)) :- _computeIdx(E,concat), _computeIdx(E,0,val(string,S1)), _computeIdx(E,1,val(string,S2)), R=@pythonStringAdd(S1,S2).

#script(python)

import constraint_handler.myClorm
import constraint_handler.evaluator

def pythonStringLength(clStr):
    pStr = myClorm.cltopy(clStr,str)
    return myClorm.pytocl(len(pStr))


def pythonStringAdd(clStr1,clStr2):
    pStr1 = myClorm.cltopy(clStr1,str)
    pStr2 = myClorm.cltopy(clStr2,str)
    return myClorm.pytocl(pStr1+pStr2)

#end.
