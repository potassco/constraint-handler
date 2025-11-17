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





%%%%%%%%%%%%%%%%% computedIdx operators
_direct_queryArgsValues(E,OP,ARGS) :- direct_query(E), E=operation(OP,ARGS). % decl operator
_direct_queryArgsValues(E,OP,ARGS) :- direct_query(E), E=operation(EOP,ARGS), eValue(EOP,function,OP).
computeIdx(E,OP) :-_direct_queryArgsValues(E,OP,ARGS).
_direct_compArg(ARGS,IDX,ARG) :- _direct_queryArgsValues(E,OP,ARGS), (IDX,ARG)=@pythonEnumerateElements(ARGS).
computeIdx(E,IDX,val(T,V)) :-_direct_queryArgsValues(E,OP,ARGS), _direct_compArg(ARGS,IDX,ARG), eValue(ARG,T,V).
eValue(E,TO,VO) :- _direct_queryArgsValues(E,OP,ARGS), computedIdx(E,val(TO,VO)).

%%%%%%%%%%%%%%%%% computed operators
_direct_queryArgsValues(E,OP,ARGS) :- direct_query(E), E=operation(OP,ARGS). % decl operator
_direct_queryArgsValues(E,OP,ARGS) :- direct_query(E), E=operation(EOP,ARGS), eValue(EOP,function,OP).
%% _direct_compArg(ARGS,IDX,ARG) :- _direct_queryArgsValues(E,OP,ARGS), (IDX,ARG)=@pythonEnumerateElements(ARGS).
%% _direct_compMapAux(ARGS,N,()) :- _direct_queryArgsValues(E,OP,ARGS), N=@pythonListLength(ARGS).
%% _direct_compMapAux(ARGS,IDX,K) :- _direct_compMapAux(ARGS,IDX+1,L), _direct_compArg(ARGS,IDX,ARG), eValue(ARG,T,V), K=(val(T,V),L).
%% compute(OP,VS) :- _direct_queryArgsValues(E,OP,ARGS), _direct_compMapAux(ARGS,0,VS).
%% eValue(E,TO,VO) :- _direct_queryArgsValues(E,OP,ARGS), _direct_compMapAux(ARGS,0,VS), computed(OP,VS,val(TO,VO)).
_direct_revMapAux(ARGS,ES,()) :- _direct_queryArgsValues(E,OP,ARGS), ES=@pythonReversed(ARGS).
_direct_revMapAux(ARGS,ES,(val(T,V),VS)) :- _direct_revMapAux(ARGS,(E,ES),VS), eValue(E,T,V).
compute(OP,VS) :- _direct_queryArgsValues(E,OP,ARGS), _direct_revMapAux(ARGS,(),VS).
eValue(E,TO,VO) :- _direct_queryArgsValues(E,OP,ARGS), _direct_revMapAux(ARGS,(),VS), computed(OP,VS,val(TO,VO)).

%%%%%%%%%%%%%%%%% lambda
_lambda_aux(LAMB,ARGS,RED) :- compute(LAMB,ARGS),
    LAMB=lambda(VARS,ERES),
    RED=@pythonBetaReduction(ERES,VARS,ARGS).

direct_query(RED) :- _lambda_aux(LAMB,ARGS,RED).
computed(LAMB,ARGS,val(TO,VO)) :- _lambda_aux(LAMB,ARGS,RED), eValue(RED,TO,VO).

%%%%%%%%%%%%%%%%% python
_direct_implode_arg(OP,ARGS,IDX,ARG) :- compute(OP,ARGS), OP=python(S), (IDX,ARG)=@pythonEnumerateElements(ARGS).
_direct_implode(ARG) :- _direct_implode_arg(OP,ARGS,IDX,ARG).
_direct_implode_args_aux(ARGS,N,()) :- compute(OP,ARGS), OP=python(S), N=@pythonListLength(ARGS).
_direct_implode_args_aux(ARGS,IDX,K) :- _direct_implode_args_aux(ARGS,IDX+1,L),
    _direct_implode_arg(OP,ARGS,IDX,ARG),
    _direct_imploded(ARG,IMP), K=(IMP,L).
_expression_eval_exec(OP,ARGS,RES) :- compute(OP,ARGS), OP=python(S), _direct_implode_args_aux(ARGS,0,L), RES = @pythonEvalExpr(operation(OP,L),(),ID), _main_solverIdentifier(ID).
computed(OP,ARGS,val(TYPE,V)) :- _expression_eval_exec(OP,ARGS,val(TYPE,V)).
warning((OP,ARGS,MSG)) :- _expression_eval_exec(OP,ARGS,error(MSG)).

%%%%%%%%%%%%%%%%% function definitions
assign(CNAME,X,lambda(VARS,EXPR)) :- define(CNAME,X,VARS,EXPR).
%direct_query(ER) :- direct_query(E), beta_reduction(E,ER).
%eValue(E,T,V) :- direct_query(E), beta_reduction(E,ER), eValue(ER,T,V).

%%%%%%%%%%%%%%%%% implode
_direct_imploded(E,val(T,V)) :- _direct_implode(E), E=val(T,V), representation(T,extensional).

_direct_imploded(E,val(T,V)) :- _direct_implode(E), E=variable(X), eValue(E,T,V).

%:- engine(NAME,E), not ensure(NAME,_), not assign(NAME,_,_).
%:- not engine(NAME,_), ensure(NAME,E).
#external usc_relax(NAME) : engine(NAME,E).
{ usc_active(NAME) } :- engine(NAME,E).
usc_active(NAME) :- engine(NAME,E), not usc_relax(NAME).
:- _se_ensure(NAME,E), not eValue(E,bool,true), usc_active(NAME).
