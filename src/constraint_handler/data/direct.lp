#defined assign/3.
#defined define/4.
#defined ensure/2.
#defined evaluate/2.

compileEnsure(CNAME,E) :- ensure(CNAME,E), engine(CNAME,compile).
compileAssign(CNAME,X,E) :- assign(CNAME,X,E), engine(CNAME,compile).

direct_query(E)      :- compileEnsure(NAME,E).
direct_query(E)      :- compileAssign(NAME,X,E).
direct_query(EX)     :- compileAssign(NAME,X,E), EX=variable(X).
direct_query(E)      :- _direct_set_assign(NAME,X,E).
direct_query(EX)     :- _direct_set_assign(NAME,X,E), EX=variable(X).
direct_query(HD)     :- direct_queries(EL), EL=(HD,TL).
direct_query(OE)     :- direct_query(E), E=operation(python(OE),EL).
direct_queries(EL) :- direct_query(E), E=operation(OP,EL), not _direct_lazy(OP).
direct_queries(TL) :- direct_queries(EL), EL=(HD,TL).

eValue(E,T,V) :- direct_query(E), E=val(T,V).


eValue(E,function,E) :- direct_query(E), E=lambda(VARS,ERES).

_lambda_aux(LAMB,ARGS,RED) :- compute(LAMB,ARGS),
    LAMB=lambda(VARS,ERES),
    L=@pythonMergeTypes2(ARGS),
    RED=@pythonBetaReduction2(ERES,VARS,L).

direct_query(RED) :- _lambda_aux(LAMB,ARGS,RED).
computed(LAMB,ARGS,TO,VO) :- _lambda_aux(LAMB,ARGS,RED), eValue(RED,TO,VO).


%eValue(E,T,V) :- direct_query(E), E=variable(X), compileAssign(NAME,X,E2), eValue(E2,T,V).
eValue(E,T,V) :- direct_query(E), E=variable(X), compileAssign(NAME,X,E2), eValue(E2,T,V), usc_active(NAME).

_direct_revMapAux(ARGS,ES,()) :- direct_query(E), E=operation(OP,ARGS),
    ES=@pythonReversed(ARGS).
_direct_revMapAux(ARGS,ES,(T,(V,(VS)))) :- _direct_revMapAux(ARGS,(E,ES),VS), eValue(E,T,V).
compute(OP,VS) :- direct_query(E), E=operation(OP,ARGS),
    _direct_revMapAux(ARGS,(),VS).
eValue(E,TO,VO) :- direct_query(E), E=operation(OP,ARGS),
    _direct_revMapAux(ARGS,(),VS),
    computed(OP,VS,TO,VO).


beta_reduction(E,ER) :- direct_query(E), E=operation(variable(OP),ARGS),
  define(_,OP,VARS,EXPR),
  ER = @pythonBetaReduction(EXPR,VARS,ARGS).
direct_query(ER)     :- direct_query(E), beta_reduction(E,ER).
eValue(E,T,V) :- direct_query(E), beta_reduction(E,ER), eValue(ER,T,V).


direct_query(E) :- _main_defaultEngine(compile), evaluate(OP,ARGS), E=operation(OP,ARGS).
evaluated(OP,ARGS,T,V) :- evaluate(OP,ARGS), E=operation(OP,ARGS), eValue(E,T,V).

%:- engine(NAME,E), not ensure(NAME,_), not assign(NAME,_,_).
%:- not engine(NAME,_), ensure(NAME,E).
#external usc_relax(NAME) : engine(NAME,E).
{ usc_active(NAME) } :- engine(NAME,E).
usc_active(NAME) :- engine(NAME,E), not usc_relax(NAME).
:- compileEnsure(NAME,E), not eValue(E,bool,true), usc_active(NAME).
