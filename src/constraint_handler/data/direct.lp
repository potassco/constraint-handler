% #include "conditionals.lp".
% #include "floats.lp".

#defined assign/3.
#defined assignToSet/3.
#defined ensure/2.

compileEnsure(CNAME,EXPR) :- ensure(CNAME,EXPR), engine(CNAME,compile).
compileAssign(CNAME,VAR,EXPR) :- assign(CNAME,VAR,EXPR), engine(CNAME,compile).
compileAssignToSet(CNAME,VAR,EXPR) :- assignToSet(CNAME,VAR,EXPR), engine(CNAME,compile).


expression(E)      :- compileEnsure(NAME,E).
expression(E)      :- compileAssign(NAME,VAR,E).
expression(EV)     :- compileAssign(NAME,VAR,E), EV=variable(VAR).
expression(E)      :- compileAssignToSet(NAME,VAR,E).
expression(EV)     :- compileAssignToSet(NAME,VAR,E), EV=variable(VAR).
expression(HD)     :- expressionList(EL), EL=(HD,TL).
expression(OE) :- expression(E), E=operation(python(OE),EL).
expressionList(EL) :- expression(E), E=operation(OP,EL).
expressionList(TL) :- expressionList(EL), EL=(HD,TL).

eValue(E,int,   C) :- expression(E), E=constant(int(C)).
eValue(E,bool,  C) :- expression(E), E=constant(bool(C)).
eValue(E,float, float(C)) :- expression(E), E=constant(float(C)).
eValue(E,str,C) :- expression(E), E=constant(str(C)).
eValue(E,symbol,C) :- expression(E), E=constant(symbol(C)).

eValue(E,T,VAL) :- expression(E), E=variable(VAR), compileAssign(NAME,VAR,E2), eValue(E2,T,VAL).

eValue(E,int,V1+V2) :- expression(E), E=operation(add, (E1,(E2,()))), eValue(E1,int,V1), eValue(E2,int,V2).
eValue(E,int,V1-V2) :- expression(E), E=operation(minus,(E1,(E2,()))), eValue(E1,int,V1), eValue(E2,int,V2).
eValue(E,int,V1*V2) :- expression(E), E=operation(mult, (E1,(E2,()))), eValue(E1,int,V1), eValue(E2,int,V2).
eValue(E,int,|V1|)  :- expression(E), E=operation(abs,  (E1,())), eValue(E1,int,V1).
eValue(E,int,-V1)   :- expression(E), E=operation(minus,(E1,())), eValue(E1,int,V1).

eValue(E,bool,true)  :- expression(E), E=operation(eq, (E1,(E2,()))), eValue(E1,int,V1), eValue(E2,int,V2), V1 =  V2.
eValue(E,bool,true)  :- expression(E), E=operation(neq,(E1,(E2,()))), eValue(E1,int,V1), eValue(E2,int,V2), V1 != V2.
eValue(E,bool,true)  :- expression(E), E=operation(leq,(E1,(E2,()))), eValue(E1,int,V1), eValue(E2,int,V2), V1 <= V2.
eValue(E,bool,true)  :- expression(E), E=operation(lt, (E1,(E2,()))), eValue(E1,int,V1), eValue(E2,int,V2), V1 <  V2.
eValue(E,bool,true)  :- expression(E), E=operation(geq,(E1,(E2,()))), eValue(E1,int,V1), eValue(E2,int,V2), V1 >= V2.
eValue(E,bool,true)  :- expression(E), E=operation(gt, (E1,(E2,()))), eValue(E1,int,V1), eValue(E2,int,V2), V1 >  V2.
eValue(E,bool,false) :- expression(E), E=operation(eq, (E1,(E2,()))), eValue(E1,int,V1), eValue(E2,int,V2), V1 != V2.
eValue(E,bool,false) :- expression(E), E=operation(neq,(E1,(E2,()))), eValue(E1,int,V1), eValue(E2,int,V2), V1 =  V2.
eValue(E,bool,false) :- expression(E), E=operation(leq,(E1,(E2,()))), eValue(E1,int,V1), eValue(E2,int,V2), V1 >  V2.
eValue(E,bool,false) :- expression(E), E=operation(lt, (E1,(E2,()))), eValue(E1,int,V1), eValue(E2,int,V2), V1 >= V2.
eValue(E,bool,false) :- expression(E), E=operation(geq,(E1,(E2,()))), eValue(E1,int,V1), eValue(E2,int,V2), V1 <  V2.
eValue(E,bool,false) :- expression(E), E=operation(gt, (E1,(E2,()))), eValue(E1,int,V1), eValue(E2,int,V2), V1 <= V2.

eValue(E,bool,true)  :- expression(E), E=operation(conj, (E1,(E2,()))), eValue(E1,bool,true),  eValue(E2,bool,true).
eValue(E,bool,false) :- expression(E), E=operation(conj, (E1,(E2,()))), eValue(E1,bool,false).
eValue(E,bool,false) :- expression(E), E=operation(conj, (E1,(E2,()))), eValue(E2,bool,false).

eValue(E,bool,true)  :- expression(E), E=operation(disj, (E1,(E2,()))), eValue(E1,bool,true).
eValue(E,bool,true)  :- expression(E), E=operation(disj, (E1,(E2,()))), eValue(E2,bool,true).
eValue(E,bool,false) :- expression(E), E=operation(disj, (E1,(E2,()))), eValue(E1,bool,false), eValue(E2,bool,false).


%#show value/3.
%#show expression/1.
