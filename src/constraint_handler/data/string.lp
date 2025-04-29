computed(O,ARGS,bool,true)  :- compute(O,ARGS), O=eq,  ARGS = (str,(S1,(str,(S2,())))), S1 =  S2.
computed(O,ARGS,bool,true)  :- compute(O,ARGS), O=neq, ARGS = (str,(S1,(str,(S2,())))), S1 != S2.
computed(O,ARGS,bool,false) :- compute(O,ARGS), O=eq,  ARGS = (str,(S1,(str,(S2,())))), S1 != S2.
computed(O,ARGS,bool,false) :- compute(O,ARGS), O=neq, ARGS = (str,(S1,(str,(S2,())))), S1 =  S2.

computed(O,ARGS,int,N) :- compute(O,ARGS), O=length, ARGS = (str,(S,())), N=@pythonStringLength(S).
computed(O,ARGS,str,R) :- compute(O,ARGS), O=concat, ARGS = (str,(S1,(str,(S2,())))), R=@pythonStringAdd(S1,S2).

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
