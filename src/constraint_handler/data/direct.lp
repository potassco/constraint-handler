#defined assign/3.
#defined define/4.
#defined ensure/2.
#defined evaluate/2.

%%%%%%%%%%%%%%%%% interface ensure/2 assign/3 evaluate/2
_se_ensure(CNAME,E) :- ensure(CNAME,E), engine(CNAME,compile).
_se_assign(CNAME,X,E) :- assign(CNAME,X,E), engine(CNAME,compile).
_se_evaluate(_se_all,OP,ARGS) :- evaluate(OP,ARGS), _main_defaultEngine(compile).

evaluated(OP,ARGS,T,V) :- _se_evaluate(CNAME,OP,ARGS), _se_value(E,val(T,V)), E=operation(OP,ARGS).


direct_query(E)  :- _se_ensure(NAME,E).
direct_query(E)  :- _se_assign(NAME,X,E).
direct_query(EX) :- _se_assign(NAME,X,E), EX=variable(X).
direct_query(E)  :- _se_evaluate(CNAME,OP,ARGS), E=operation(OP,ARGS).
direct_query(SE) :- direct_query(E), E=operation(OP,ES), not _direct_lazy(OP), SE=@pythonListElements(ES).

_se_value(E,E) :- direct_query(E), E=val(T,V).


_se_value(E,val(function,E)) :- direct_query(E), E=lambda(VARS,ERES).

_se_value(E,V) :- direct_query(E), E=variable(X), _se_assign(NAME,X,E2), _se_value(E2,V), usc_active(NAME).





%%%%%%%%%%%%%%%%% computedIdx operators
_direct_queryArgsValues(E,OP,ARGS) :- direct_query(E), E=operation(OP,ARGS). % decl operator
_direct_queryArgsValues(E,OP,ARGS) :- direct_query(E), E=operation(EOP,ARGS), _se_value(EOP,val(function,OP)).
computeIdx(E,OP) :-_direct_queryArgsValues(E,OP,ARGS).
_direct_compArg(ARGS,IDX,ARG) :- _direct_queryArgsValues(E,OP,ARGS), (IDX,ARG)=@pythonEnumerateElements(ARGS).
computeIdx(E,IDX,V) :-_direct_queryArgsValues(E,OP,ARGS), _direct_compArg(ARGS,IDX,ARG), _se_value(ARG,V).
_se_value(E,VO) :- _direct_queryArgsValues(E,OP,ARGS), computedIdx(E,VO).

%%%%%%%%%%%%%%%%% computed operators
_direct_queryArgsValues(E,OP,ARGS) :- direct_query(E), E=operation(OP,ARGS). % decl operator
_direct_queryArgsValues(E,OP,ARGS) :- direct_query(E), E=operation(EOP,ARGS), _se_value(EOP,val(function,OP)).
%% _direct_compArg(ARGS,IDX,ARG) :- _direct_queryArgsValues(E,OP,ARGS), (IDX,ARG)=@pythonEnumerateElements(ARGS).
%% _direct_compMapAux(ARGS,N,()) :- _direct_queryArgsValues(E,OP,ARGS), N=@pythonListLength(ARGS).
%% _direct_compMapAux(ARGS,IDX,K) :- _direct_compMapAux(ARGS,IDX+1,L), _direct_compArg(ARGS,IDX,ARG), _se_value(ARG,T,V), K=(val(T,V),L).
%% compute(OP,VS) :- _direct_queryArgsValues(E,OP,ARGS), _direct_compMapAux(ARGS,0,VS).
%% _se_value(E,TO,VO) :- _direct_queryArgsValues(E,OP,ARGS), _direct_compMapAux(ARGS,0,VS), computed(OP,VS,val(TO,VO)).
_direct_revMapAux(ARGS,ES,()) :- _direct_queryArgsValues(E,OP,ARGS), ES=@pythonReversed(ARGS).
_direct_revMapAux(ARGS,ES,(V,VS)) :- _direct_revMapAux(ARGS,(E,ES),VS), _se_value(E,V).
compute(OP,VS) :- _direct_queryArgsValues(E,OP,ARGS), _direct_revMapAux(ARGS,(),VS).
_se_value(E,VO) :- _direct_queryArgsValues(E,OP,ARGS), _direct_revMapAux(ARGS,(),VS), computed(OP,VS,VO).

%%%%%%%%%%%%%%%%% lambda
_lambda_aux(LAMB,ARGS,RED) :- compute(LAMB,ARGS),
    LAMB=lambda(VARS,ERES),
    RED=@pythonBetaReduction(ERES,VARS,ARGS).

direct_query(RED) :- _lambda_aux(LAMB,ARGS,RED).
computed(LAMB,ARGS,VO) :- _lambda_aux(LAMB,ARGS,RED), _se_value(RED,VO).

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
%_se_value(E,T,V) :- direct_query(E), beta_reduction(E,ER), _se_value(ER,T,V).

%%%%%%%%%%%%%%%%% implode
_direct_imploded(E,E) :- _direct_implode(E), E=val(T,V), representation(T,extensional).

_direct_imploded(E,V) :- _direct_implode(E), E=variable(X), _se_value(E,V).

%:- engine(NAME,E), not ensure(NAME,_), not assign(NAME,_,_).
%:- not engine(NAME,_), ensure(NAME,E).
#external usc_relax(NAME) : engine(NAME,E).
{ usc_active(NAME) } :- engine(NAME,E).
usc_active(NAME) :- engine(NAME,E), not usc_relax(NAME).
:- _se_ensure(NAME,E), not _se_value(E,val(bool,true)), usc_active(NAME).
