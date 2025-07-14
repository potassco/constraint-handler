#defined assign/3.
#defined assignToSet/3.
#defined ensure/2.
#defined evaluate/2.

compileEnsure(CNAME,E) :- ensure(CNAME,E), engine(CNAME,compile).
compileAssign(CNAME,X,E) :- assign(CNAME,X,E), engine(CNAME,compile).
_set_compileAssign(CNAME,X,E) :- set_assign(CNAME,X,E), engine(CNAME,compile).


direct_query(E)      :- compileEnsure(NAME,E).
direct_query(E)      :- compileAssign(NAME,X,E).
direct_query(EX)     :- compileAssign(NAME,X,E), EX=variable(X).
direct_query(E)      :- _set_compileAssign(NAME,X,E).
direct_query(EX)     :- _set_compileAssign(NAME,X,E), EX=variable(X).
direct_query(HD)     :- direct_queries(EL), EL=(HD,TL).
direct_query(OE)     :- direct_query(E), E=operation(python(OE),EL).
direct_queries(EL) :- direct_query(E), E=operation(OP,EL).
direct_queries(TL) :- direct_queries(EL), EL=(HD,TL).

eValue(E,T,V) :- direct_query(E), E=val(T,V).

%eValue(E,T,V) :- direct_query(E), E=variable(X), compileAssign(NAME,X,E2), eValue(E2,T,V).
eValue(E,T,V) :- direct_query(E), E=variable(X), compileAssign(NAME,X,E2), eValue(E2,T,V), usc_active(NAME).

_direct_revMapAux(ARGS,ES,()) :- direct_query(E), E=operation(OP,ARGS),
    ES=@pythonReversed(ARGS). %,
_direct_revMapAux(ARGS,ES,(T,(V,(VS)))) :- _direct_revMapAux(ARGS,(E,ES),VS), eValue(E,T,V).
compute(OP,VS) :- direct_query(E), E=operation(OP,ARGS),
    _direct_revMapAux(ARGS,(),VS).
eValue(E,TO,VO) :- direct_query(E), E=operation(OP,ARGS),
    _direct_revMapAux(ARGS,(),VS),
    computed(OP,VS,TO,VO).

direct_query(E) :- evaluate(OP,ARGS), E=operation(OP,ARGS).
evaluated(OP,ARGS,T,V) :- evaluate(OP,ARGS), E=operation(OP,ARGS), eValue(E,T,V).

%:- engine(NAME,E), not ensure(NAME,_), not assign(NAME,_,_).
%:- not engine(NAME,_), ensure(NAME,E).
#external usc_relax(NAME) : engine(NAME,E).
{ usc_active(NAME) } :- engine(NAME,E).
usc_active(NAME) :- engine(NAME,E), not usc_relax(NAME).
:- compileEnsure(NAME,E), not eValue(E,bool,true), usc_active(NAME).
