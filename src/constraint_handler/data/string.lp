%%%%%%%%%%%%%%%%% eq neq
operator_declare(OP,(T,(T,())),bool) :- T = str, OP = (eq;neq).
_computed(O,ARGS,val(bool,true))  :- _compute(O,ARGS), O=eq,  ARGS = (val(str,S1),(val(str,S2),())), S1 =  S2.
_computed(O,ARGS,val(bool,true))  :- _compute(O,ARGS), O=neq, ARGS = (val(str,S1),(val(str,S2),())), S1 != S2.
_computed(O,ARGS,val(bool,false)) :- _compute(O,ARGS), O=eq,  ARGS = (val(str,S1),(val(str,S2),())), S1 != S2.
_computed(O,ARGS,val(bool,false)) :- _compute(O,ARGS), O=neq, ARGS = (val(str,S1),(val(str,S2),())), S1 =  S2.

%%%%%%%%%%%%%%%%% length concat
operator_declare(OP,(T,()),int) :- T = str, OP = length.
operator_declare(OP,(T,(T,())),T) :- T = str, OP = concat.
_computed(O,ARGS,val(int,N)) :- _compute(O,ARGS), O=length, ARGS = (val(str,S),()), N=@pythonStringLength(S).
_computed(O,ARGS,val(str,R)) :- _compute(O,ARGS), O=concat, ARGS = (val(str,S1),(val(str,S2),())), R=@pythonStringAdd(S1,S2).

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
