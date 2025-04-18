eValue(E,bool,true)  :- expression(E), E=operation(eq, (E1,(E2,()))), eValue(E1,str,V1), eValue(E2,str,V2), V1 =  V2.
eValue(E,bool,true)  :- expression(E), E=operation(neq,(E1,(E2,()))), eValue(E1,str,V1), eValue(E2,str,V2), V1 != V2.
eValue(E,bool,false) :- expression(E), E=operation(eq, (E1,(E2,()))), eValue(E1,str,V1), eValue(E2,str,V2), V1 != V2.
eValue(E,bool,false) :- expression(E), E=operation(neq,(E1,(E2,()))), eValue(E1,str,V1), eValue(E2,str,V2), V1 =  V2.

eValue(E,int,N)  :- expression(E), E=operation(length,(E1,())), eValue(E1,str,S), N=@pythonStringLength(S).
eValue(E,str,RES):- expression(E), E=operation(add,(E1,(E2,()))), eValue(E1,str,S1), eValue(E2,str,S2), RES=@pythonStringAdd(S1,S2).

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
