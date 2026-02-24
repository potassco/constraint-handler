#defined assign/3.
#defined define/4.
#defined ensure/2.
#defined evaluate/2.

%%%%%%%%%%%%%%%%% interface ensure/2 assign/3 evaluate/2
_se_ensure(CNAME,E) :- ensure(CNAME,E), engine(CNAME,compile).
_se_assign(CNAME,variable(X),E) :- assign(CNAME,X,E), engine(CNAME,compile).
_se_evaluate(_se_all,OP,ARGS) :- evaluate(OP,ARGS), _main_defaultEngine(compile).

evaluated(OP,ARGS,V) :- _se_evaluate(CNAME,OP,ARGS), _se_value(E,V), E=operation(OP,ARGS).


direct_query(E)  :- _se_ensure(NAME,E).
direct_query(E)  :- _se_assign(NAME,X,E).
direct_query(X)  :- _se_assign(NAME,X,E).
direct_query(E)  :- _se_evaluate(CNAME,OP,ARGS), E=operation(OP,ARGS).
direct_query(SE) :- direct_query(E), E=operation(OP,ES), not _direct_lazy(OP), SE=@pythonListElements(ES).

_se_value(E,E) :- direct_query(E), E=val(T,V).


_se_value(E,val(function,E)) :- direct_query(E), E=lambda(VARS,ERES).

_se_value(E,V) :- direct_query(E), E=variable(X), _se_assign(NAME,E,E2), _se_value(E2,V), usc_active(NAME).





%%%%%%%%%%%%%%%%% _computedIdx operators
_direct_queryArgsValues(E,OP,ARGS) :- direct_query(E), E=operation(OP,ARGS). % decl operator
_direct_queryArgsValues(E,OP,ARGS) :- direct_query(E), E=operation(EOP,ARGS), _se_value(EOP,val(function,OP)).
_computeIdx(E,OP) :-_direct_queryArgsValues(E,OP,ARGS).
_direct_compArg(ARGS,IDX,ARG) :- _direct_queryArgsValues(E,OP,ARGS), (IDX,ARG)=@pythonEnumerateElements(ARGS).
_computeIdx(E,IDX,V) :-_direct_queryArgsValues(E,OP,ARGS), _direct_compArg(ARGS,IDX,ARG), _se_value(ARG,V).
_se_value(E,VO) :- _direct_queryArgsValues(E,OP,ARGS), _computedIdx(E,VO).

%%%%%%%%%%%%%%%%% _computed operators
_direct_queryArgsValues(E,OP,ARGS) :- direct_query(E), E=operation(OP,ARGS). % decl operator
_direct_queryArgsValues(E,OP,ARGS) :- direct_query(E), E=operation(EOP,ARGS), _se_value(EOP,val(function,OP)).
% Some operators should not build the full evaluated argument tuple `VS` via
% _direct_revMapAux/3 because this can create Cartesian-product grounding
% blowups (one rule instance per combination of argument values). Such
% operators are expected to provide results via _computedIdx/2 (or another
% specialized route).
%
% Positive gate: tuple-building is allowed only when needed.
% For `add`, enable tuple-building if at least one argument is not statically
% typed as int. Integer-only adds can be handled cheaply via _computedIdx/2.
_direct_doCompute(OP, ARGS) :- _direct_queryArgsValues(E, OP, ARGS), OP != add.
_direct_doCompute(add, ARGS) :- _direct_queryArgsValues(E, add, ARGS),
    (_, ARG) = @pythonEnumerateElements(ARGS), type_expression((), ARG, T), T != int.
%% _direct_compArg(ARGS,IDX,ARG) :- _direct_queryArgsValues(E,OP,ARGS), (IDX,ARG)=@pythonEnumerateElements(ARGS).
%% _direct_compMapAux(ARGS,N,()) :- _direct_queryArgsValues(E,OP,ARGS), N=@pythonListLength(ARGS).
%% _direct_compMapAux(ARGS,IDX,K) :- _direct_compMapAux(ARGS,IDX+1,L), _direct_compArg(ARGS,IDX,ARG), _se_value(ARG,T,V), K=(val(T,V),L).
%% _compute(OP,VS) :- _direct_queryArgsValues(E,OP,ARGS), _direct_compMapAux(ARGS,0,VS).
%% _se_value(E,TO,VO) :- _direct_queryArgsValues(E,OP,ARGS), _direct_compMapAux(ARGS,0,VS), _computed(OP,VS,val(TO,VO)).
_direct_revMapAux(ARGS,ES,()) :- _direct_queryArgsValues(E,OP,ARGS), _direct_doCompute(OP, ARGS), ES=@pythonReversed(ARGS).
_direct_revMapAux(ARGS,ES,(V,VS)) :- _direct_revMapAux(ARGS,(E,ES),VS), _se_value(E,V).
_compute(OP,VS) :- _direct_queryArgsValues(E,OP,ARGS), _direct_doCompute(OP, ARGS), _direct_revMapAux(ARGS,(),VS).
_se_value(E,VO) :- _direct_queryArgsValues(E,OP,ARGS), _direct_doCompute(OP, ARGS), _direct_revMapAux(ARGS,(),VS), _computed(OP,VS,VO).

%%%%%%%%%%%%%%%%% lambda
_lambda_aux(LAMB,ARGS,RED) :- _compute(LAMB,ARGS),
    LAMB=lambda(VARS,ERES),
    RED=@pythonBetaReduction(ERES,VARS,ARGS).

direct_query(RED) :- _lambda_aux(LAMB,ARGS,RED).
_computed(LAMB,ARGS,VO) :- _lambda_aux(LAMB,ARGS,RED), _se_value(RED,VO).

%%%%%%%%%%%%%%%%% python
_direct_implode_arg(OP,ARGS,IDX,ARG) :- _compute(OP,ARGS), OP=python(S), (IDX,ARG)=@pythonEnumerateElements(ARGS).
_direct_implode(ARG) :- _direct_implode_arg(OP,ARGS,IDX,ARG).
_direct_implode_args_aux(ARGS,N,()) :- _compute(OP,ARGS), OP=python(S), N=@pythonListLength(ARGS).
_direct_implode_args_aux(ARGS,IDX,K) :- _direct_implode_args_aux(ARGS,IDX+1,L),
    _direct_implode_arg(OP,ARGS,IDX,ARG),
    _direct_imploded(ARG,IMP), K=(IMP,L).
_expression_eval_exec(OP,ARGS,RES) :- _compute(OP,ARGS), OP=python(S), _direct_implode_args_aux(ARGS,0,L), RES = @pythonEvalExpr(operation(OP,L),(),ID), _main_solverIdentifier(ID).
_computed(OP,ARGS,val(TYPE,V)) :- _expression_eval_exec(OP,ARGS,val(TYPE,V)).
_computed(OP,ARGS,bad) :- _expression_eval_exec(OP,ARGS,error(KIND,MSG)).
_warning(KIND,(),(OP,ARGS,MSG)) :- _expression_eval_exec(OP,ARGS,error(KIND,MSG)).
%%% TODO duplicated code in groundEval.lp

%%%%%%%%%%%%%%%%% function definitions
assign(CNAME,X,lambda(VARS,EXPR)) :- define(CNAME,X,VARS,EXPR).
%direct_query(ER) :- direct_query(E), beta_reduction(E,ER).
%_se_value(E,T,V) :- direct_query(E), beta_reduction(E,ER), _se_value(ER,T,V).

%%%%%%%%%%%%%%%%% bad
_se_value(E,bad) :- direct_query(E), E=operation(OP,ARGS), _se_value(ARG,bad), ARG=@pythonListElements(ARGS).
_se_value(E,bad) :- direct_query(E), E=operation(OP,ARGS), _se_value(OP,bad).
_se_value(E,bad) :- direct_query(E), E=bad.

%%%%%%%%%%%%%%%%% implode
_direct_imploded(E,E) :- _direct_implode(E), E=val(T,V), representation(T,extensional).

_direct_imploded(E,V) :- _direct_implode(E), E=variable(X), _se_value(E,V).

engine(_internal,compile).
%:- engine(NAME,E), not ensure(NAME,_), not assign(NAME,_,_).
%:- not engine(NAME,_), ensure(NAME,E).
#external usc_relax(NAME) : engine(NAME,E).
{ usc_active(NAME) } :- engine(NAME,E).
usc_active(NAME) :- engine(NAME,E), not usc_relax(NAME).
:- _se_ensure(NAME,E), not _se_value(E,val(bool,true)), not _se_value(E,bad), usc_active(NAME).
