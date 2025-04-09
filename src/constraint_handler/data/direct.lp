% #include "conditionals.lp".
% #include "floats.lp".

#defined assign/3.
#defined assignToSet/3.
#defined ensure/2.

compileEnsure(CNAME,E) :- ensure(CNAME,E), engine(CNAME,compile).
compileAssign(CNAME,X,E) :- assign(CNAME,X,E), engine(CNAME,compile).
compileAssignToSet(CNAME,X,E) :- assignToSet(CNAME,X,E), engine(CNAME,compile).


expression(E)      :- compileEnsure(NAME,E).
expression(E)      :- compileAssign(NAME,X,E).
expression(EX)     :- compileAssign(NAME,X,E), EX=variable(X).
expression(E)      :- compileAssignToSet(NAME,X,E).
expression(EX)     :- compileAssignToSet(NAME,X,E), EX=variable(X).
expression(HD)     :- expressionList(EL), EL=(HD,TL).
expression(OE) :- expression(E), E=operation(python(OE),EL).
expressionList(EL) :- expression(E), E=operation(OP,EL).
expressionList(TL) :- expressionList(EL), EL=(HD,TL).

eValue(E,int,   C) :- expression(E), E=constant(int(C)).
eValue(E,bool,  C) :- expression(E), E=constant(bool(C)).
eValue(E,float, float(C)) :- expression(E), E=constant(float(C)).
eValue(E,str,C) :- expression(E), E=constant(str(C)).
eValue(E,symbol,C) :- expression(E), E=constant(symbol(C)).

eValue(E,T,V) :- expression(E), E=variable(X), compileAssign(NAME,X,E2), eValue(E2,T,V).

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
