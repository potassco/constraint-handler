% #include "conditionals.lp".
% #include "floats.lp".

#defined assign/3.
#defined assignToSet/3.
#defined ensure/2.
#defined evaluate/2.

compileEnsure(CNAME,E) :- ensure(CNAME,E), engine(CNAME,compile).
compileAssign(CNAME,X,E) :- assign(CNAME,X,E), engine(CNAME,compile).
_set_compileAssign(CNAME,X,E) :- set_assign(CNAME,X,E), engine(CNAME,compile).


expression(E)      :- compileEnsure(NAME,E).
expression(E)      :- compileAssign(NAME,X,E).
expression(EX)     :- compileAssign(NAME,X,E), EX=variable(X).
expression(E)      :- _set_compileAssign(NAME,X,E).
expression(EX)     :- _set_compileAssign(NAME,X,E), EX=variable(X).
expression(HD)     :- expressionList(EL), EL=(HD,TL).
expression(OE) :- expression(E), E=operation(python(OE),EL).
expressionList(EL) :- expression(E), E=operation(OP,EL).
expressionList(TL) :- expressionList(EL), EL=(HD,TL).

eValue(E,int,   C) :- expression(E), E=constant(int(C)).
eValue(E,bool,  C) :- expression(E), E=constant(bool(C)).
eValue(E,float, float(C)) :- expression(E), E=constant(float(C)).
eValue(E,str,C) :- expression(E), E=constant(str(C)).
eValue(E,symbol,C) :- expression(E), E=constant(symbol(C)).

eValue(E,T,V) :- expression(E), E=val(T,V).

eValue(E,T,V) :- expression(E), E=variable(X), compileAssign(NAME,X,E2), eValue(E2,T,V).

_direct_revMapAux(ARGS,ES,()) :- expression(E), E=operation(OP,ARGS),
    ES=@pythonReversed(ARGS). %,
_direct_revMapAux(ARGS,ES,(T,(V,(VS)))) :- _direct_revMapAux(ARGS,(E,ES),VS), eValue(E,T,V).
compute(OP,VS) :- expression(E), E=operation(OP,ARGS),
    _direct_revMapAux(ARGS,(),VS).
eValue(E,TO,VO) :- expression(E), E=operation(OP,ARGS),
    _direct_revMapAux(ARGS,(),VS),
    computed(OP,VS,TO,VO).

expression(E) :- evaluate(NAME,E).
evaluated(E,T,V) :- evaluate(NAME,E), eValue(E,T,V).