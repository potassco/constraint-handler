%%%%%%%%%%%%%%%%% eq neq
operator_declare((eq;neq),(str,(str,())),bool).
_computed(eq,(val(str,S1),(val(str,S2),())),val(bool,true))   :- _compute(eq,(val(str,S1),(val(str,S2),()))),  S1 =  S2.
_computed(neq,(val(str,S1),(val(str,S2),())),val(bool,true))  :- _compute(neq,(val(str,S1),(val(str,S2),()))), S1 != S2.
_computed(eq,(val(str,S1),(val(str,S2),())),val(bool,false))  :- _compute(eq,(val(str,S1),(val(str,S2),()))),  S1 != S2.
_computed(neq,(val(str,S1),(val(str,S2),())),val(bool,false)) :- _compute(neq,(val(str,S1),(val(str,S2),()))), S1 =  S2.

%%%%%%%%%%%%%%%%% length concat
operator_declare(length,(str,()),int).
operator_declare(concat,(str,(str,())),str).
_computedIdx(E,val(int,N)) :- _computeIdx(E,length), _computeIdx(E,0,val(str,S)), N=@pythonStringLength(S).
_computedIdx(E,val(str,R)) :- _computeIdx(E,concat), _computeIdx(E,0,val(str,S1)), _computeIdx(E,1,val(str,S2)), R=@pythonStringAdd(S1,S2).

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
