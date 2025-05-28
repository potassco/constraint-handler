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
expression(OE)     :- expression(E), E=operation(python(OE),EL).
expressionList(EL) :- expression(E), E=operation(OP,EL).
expressionList(TL) :- expressionList(EL), EL=(HD,TL).

eValue(E,int,   C) :- expression(E), E=constant(int(C)).
eValue(E,bool,  C) :- expression(E), E=constant(bool(C)).
eValue(E,float, float(C)) :- expression(E), E=constant(float(C)).
eValue(E,str,C) :- expression(E), E=constant(str(C)).
eValue(E,symbol,C) :- expression(E), E=constant(symbol(C)).

eValue(E,T,V) :- expression(E), E=val(T,V).

%eValue(E,T,V) :- expression(E), E=variable(X), compileAssign(NAME,X,E2), eValue(E2,T,V).
eValue(E,T,V) :- expression(E), E=variable(X), compileAssign(NAME,X,E2), eValue(E2,T,V), usc_active(NAME).

_direct_revMapAux(ARGS,ES,()) :- expression(E), E=operation(OP,ARGS),
    ES=@pythonReversed(ARGS). %,
_direct_revMapAux(ARGS,ES,(T,(V,(VS)))) :- _direct_revMapAux(ARGS,(E,ES),VS), eValue(E,T,V).
compute(OP,VS) :- expression(E), E=operation(OP,ARGS),
    _direct_revMapAux(ARGS,(),VS).
eValue(E,TO,VO) :- expression(E), E=operation(OP,ARGS),
    _direct_revMapAux(ARGS,(),VS),
    computed(OP,VS,TO,VO).

expression(E) :- evaluate(OP,ARGS), E=operation(OP,ARGS).
evaluated(OP,ARGS,T,V) :- evaluate(OP,ARGS), E=operation(OP,ARGS), eValue(E,T,V).

%:- engine(NAME,E), not ensure(NAME,_), not assign(NAME,_,_).
%:- not engine(NAME,_), ensure(NAME,E).
#external usc_relax(NAME) : engine(NAME,E).
{ usc_active(NAME) } :- engine(NAME,E).
usc_active(NAME) :- engine(NAME,E), not usc_relax(NAME).
:- compileEnsure(NAME,E), not eValue(E,bool,true), usc_active(NAME).
