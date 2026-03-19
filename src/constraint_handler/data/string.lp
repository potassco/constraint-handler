%%%%%%%%%%%%%%%%% length concat
operator_declare(OP,(T,()),int) :- T = str, OP = length.
operator_declare(OP,(T,(T,())),T) :- T = str, OP = concat.
_computedIdx_id(E_ID,val(int,N)) :- _computeIdx_id(E_ID, length), _computeIdx_id(E_ID, 0, val(str, S)), N=@pythonStringLength(S).
_computedIdx_id(E_ID,val(str,R)) :- _computeIdx_id(E_ID, concat), _computeIdx_id(E_ID, 0, val(str, S1)), _computeIdx_id(E_ID, 1, val(str, S2)), R=@pythonStringAdd(S1,S2).

#script(python)

import constraint_handler.myClorm
import constraint_handler.evaluator

def pythonStringLength(clStr):
    pStr = myClorm.cltopy(clStr)
    return myClorm.pytocl(len(pStr))


def pythonStringAdd(clStr1,clStr2):
    pStr1 = myClorm.cltopy(clStr1)
    pStr2 = myClorm.cltopy(clStr2)
    return myClorm.pytocl(pStr1+pStr2)

#end.
