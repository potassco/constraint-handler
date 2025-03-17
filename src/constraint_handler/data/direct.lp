% #include "conditionals.lp".
% #include "floats.lp".

#defined assign/3.
#defined ensure/2.

compileEnsure(CNAME,EXPR) :- ensure(CNAME,EXPR), engine(CNAME,compile).
compileAssign(CNAME,VAR,EXPR) :- assign(CNAME,VAR,EXPR), engine(CNAME,compile).


expression(E)      :- compileEnsure(NAME,E).
expression(E)      :- compileAssign(NAME,VAR,E).
expression(EV)     :- compileAssign(NAME,VAR,E), EV=variable(VAR).
expression(HD)     :- expressionList(EL), EL=(HD,TL).
expression(OE) :- expression(E), E=operation(python(OE),EL).
expressionList(EL) :- expression(E), E=operation(OP,EL).
expressionList(TL) :- expressionList(EL), EL=(HD,TL).

value(E,int,   C) :- expression(E), E=constant(int(C)).
value(E,bool,  C) :- expression(E), E=constant(bool(C)).
value(E,float, float(C)) :- expression(E), E=constant(float(C)).
value(E,str,C) :- expression(E), E=constant(str(C)).
value(E,symbol,C) :- expression(E), E=constant(symbol(C)).

value(E,T,VAL) :- expression(E), E=variable(VAR), compileAssign(NAME,VAR,E2), value(E2,T,VAL).

value(E,int,V1+V2) :- expression(E), E=operation(plus, (E1,(E2,()))), value(E1,int,V1), value(E2,int,V2).
value(E,int,V1-V2) :- expression(E), E=operation(minus,(E1,(E2,()))), value(E1,int,V1), value(E2,int,V2).
value(E,int,V1*V2) :- expression(E), E=operation(mult, (E1,(E2,()))), value(E1,int,V1), value(E2,int,V2).
value(E,int,|V1|)  :- expression(E), E=operation(abs,  (E1,())), value(E1,int,V1).
value(E,int,-V1)   :- expression(E), E=operation(minus,(E1,())), value(E1,int,V1).

value(E,bool,true)  :- expression(E), E=operation(eq, (E1,(E2,()))), value(E1,int,V1), value(E2,int,V2), V1 =  V2.
value(E,bool,true)  :- expression(E), E=operation(neq,(E1,(E2,()))), value(E1,int,V1), value(E2,int,V2), V1 != V2.
value(E,bool,true)  :- expression(E), E=operation(leq,(E1,(E2,()))), value(E1,int,V1), value(E2,int,V2), V1 <= V2.
value(E,bool,true)  :- expression(E), E=operation(lt, (E1,(E2,()))), value(E1,int,V1), value(E2,int,V2), V1 <  V2.
value(E,bool,true)  :- expression(E), E=operation(geq,(E1,(E2,()))), value(E1,int,V1), value(E2,int,V2), V1 >= V2.
value(E,bool,true)  :- expression(E), E=operation(gt, (E1,(E2,()))), value(E1,int,V1), value(E2,int,V2), V1 >  V2.
value(E,bool,false) :- expression(E), E=operation(eq, (E1,(E2,()))), value(E1,int,V1), value(E2,int,V2), V1 != V2.
value(E,bool,false) :- expression(E), E=operation(neq,(E1,(E2,()))), value(E1,int,V1), value(E2,int,V2), V1 =  V2.
value(E,bool,false) :- expression(E), E=operation(leq,(E1,(E2,()))), value(E1,int,V1), value(E2,int,V2), V1 >  V2.
value(E,bool,false) :- expression(E), E=operation(lt, (E1,(E2,()))), value(E1,int,V1), value(E2,int,V2), V1 >= V2.
value(E,bool,false) :- expression(E), E=operation(geq,(E1,(E2,()))), value(E1,int,V1), value(E2,int,V2), V1 <  V2.
value(E,bool,false) :- expression(E), E=operation(gt, (E1,(E2,()))), value(E1,int,V1), value(E2,int,V2), V1 <= V2.

value(E,bool,true)  :- expression(E), E=operation(conj, (E1,(E2,()))), value(E1,bool,true),  value(E2,bool,true).
value(E,bool,false) :- expression(E), E=operation(conj, (E1,(E2,()))), value(E1,bool,false).
value(E,bool,false) :- expression(E), E=operation(conj, (E1,(E2,()))), value(E2,bool,false).

value(E,bool,true)  :- expression(E), E=operation(disj, (E1,(E2,()))), value(E1,bool,true).
value(E,bool,true)  :- expression(E), E=operation(disj, (E1,(E2,()))), value(E2,bool,true).
value(E,bool,false) :- expression(E), E=operation(disj, (E1,(E2,()))), value(E1,bool,false), value(E2,bool,false).


%#show value/3.
%#show expression/1.
