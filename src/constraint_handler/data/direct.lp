#defined assign/3.
#defined define/4.
#defined ensure/2.
#defined evaluate/2.

%%%%%%%%%%%%%%%%% interface ensure/2 assign/3 evaluate/2
_se_ensure(CNAME,E) :- ensure(CNAME,E), engine(CNAME,compile).
_se_assign(CNAME,X,E) :- assign(CNAME,X,E), engine(CNAME,compile).
_se_evaluate(_se_all,OP,ARGS) :- evaluate(OP,ARGS), _main_defaultEngine(compile).

evaluated(OP,ARGS,T,V) :- _se_evaluate(CNAME,OP,ARGS), eValue(E,T,V), E=operation(OP,ARGS).


direct_query(E)  :- _se_ensure(NAME,E).
direct_query(E)  :- _se_assign(NAME,X,E).
direct_query(EX) :- _se_assign(NAME,X,E), EX=variable(X).
direct_query(E)  :- _se_evaluate(CNAME,OP,ARGS), E=operation(OP,ARGS).
direct_query(SE) :- direct_query(E), E=operation(OP,ES), not _direct_lazy(OP), SE=@pythonListElements(ES).

eValue(E,T,V) :- direct_query(E), E=val(T,V).


eValue(E,function,E) :- direct_query(E), E=lambda(VARS,ERES).

eValue(E,T,V) :- direct_query(E), E=variable(X), _se_assign(NAME,X,E2), eValue(E2,T,V), usc_active(NAME).

%%%%%%%%%%%%%%%%% computed operators
_direct_revMapAux(ARGS,ES,()) :- direct_query(E), E=operation(OP,ARGS),
    ES=@pythonReversed(ARGS).
_direct_revMapAux(ARGS,ES,(T,(V,(VS)))) :- _direct_revMapAux(ARGS,(E,ES),VS), eValue(E,T,V).
compute(OP,VS) :- direct_query(E), E=operation(OP,ARGS),
    _direct_revMapAux(ARGS,(),VS).
eValue(E,TO,VO) :- direct_query(E), E=operation(OP,ARGS),
    _direct_revMapAux(ARGS,(),VS),
    computed(OP,VS,TO,VO).


%%%%%%%%%%%%%%%%% lambda
_lambda_aux(LAMB,ARGS,RED) :- compute(LAMB,ARGS),
    LAMB=lambda(VARS,ERES),
    RED=@pythonBetaReduction2(ERES,VARS,ARGS).

direct_query(RED) :- _lambda_aux(LAMB,ARGS,RED).
computed(LAMB,ARGS,TO,VO) :- _lambda_aux(LAMB,ARGS,RED), eValue(RED,TO,VO).

%%%%%%%%%%%%%%%%% python
computed(OP,ARGS,T,RES) :- compute(OP,ARGS), OP=python(S), L=@pythonMergeTypes(ARGS), (T,RES) = @pythonEvalOperator(OP,L).


%%%%%%%%%%%%%%%%% variable (define)
beta_reduction(E,ER) :- direct_query(E), E=operation(variable(OP),ARGS),
  define(_,OP,VARS,EXPR),
  ER = @pythonBetaReduction(EXPR,VARS,ARGS).
direct_query(ER)     :- direct_query(E), beta_reduction(E,ER).
eValue(E,T,V) :- direct_query(E), beta_reduction(E,ER), eValue(ER,T,V).



%:- engine(NAME,E), not ensure(NAME,_), not assign(NAME,_,_).
%:- not engine(NAME,_), ensure(NAME,E).
#external usc_relax(NAME) : engine(NAME,E).
{ usc_active(NAME) } :- engine(NAME,E).
usc_active(NAME) :- engine(NAME,E), not usc_relax(NAME).
:- _se_ensure(NAME,E), not eValue(E,bool,true), usc_active(NAME).
