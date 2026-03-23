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

_se_value(E,E) :- direct_query(E), E=val(_,_).
_se_value(E,E) :- direct_query(E), E=ref(_,_).


_se_value(E,val(function,E)) :- direct_query(E), E=lambda(VARS,ERES).

_se_value(E,V) :- direct_query(E), E=variable(X), _se_assign(NAME,E,E2), _se_value(E2,V), usc_active(NAME).





%%%%%%%%%%%%%%%%% _computedIdx operators
_direct_queryArgsValues(E,OP,ARGS) :- direct_query(E), E=operation(OP,ARGS). % decl operator
_direct_queryArgsValues(E,OP,ARGS) :- direct_query(E), E=operation(EOP,ARGS), _se_value(EOP,val(function,OP)).
_computeIdx(E,OP) :-_direct_queryArgsValues(E,OP,ARGS).
_length(E,LEN) :- _direct_queryArgsValues(E,_,ARGS), LEN=@pythonListLength(ARGS).
_direct_compArg(ARGS,IDX,ARG) :- _direct_queryArgsValues(E,OP,ARGS), (IDX,ARG)=@pythonEnumerateElements(ARGS).
_computeIdx(E,IDX,V) :-_direct_queryArgsValues(E,OP,ARGS), _direct_compArg(ARGS,IDX,ARG), _se_value(ARG,V).
_se_value(E,VO) :- _direct_queryArgsValues(E,OP,ARGS), _computedIdx(E,VO).

%%%%%%%%%%%%%%%%% argument-list helpers (compile engine)
% Only needed for lambda application. Guarding this prevents grounding
% all argument combinations for every operation.
_direct_needs_args_list(E) :- _direct_queryArgsValues(E,OP,_), OP=lambda(_,_).

_direct_args_list_aux(E,IDX,()) :- _direct_needs_args_list(E), _length(E,IDX).
_direct_args_list_aux(E,IDX,(V,VS)) :- _direct_needs_args_list(E), _direct_args_list_aux(E,IDX+1,VS), _computeIdx(E,IDX,V).
_direct_args_list(E,VS) :- _direct_needs_args_list(E), _direct_args_list_aux(E,0,VS).

%%%%%%%%%%%%%%%%% lambda application
_lambda_aux(E,RED) :- _computeIdx(E,LAMB),
    LAMB=lambda(VARS,ERES),
    _direct_args_list(E,ARGS),
    RED=@pythonBetaReduction(ERES,VARS,ARGS).

direct_query(RED) :- _lambda_aux(E,RED).
_computedIdx(E,VO) :- _lambda_aux(E,RED), _se_value(RED,VO).

%%%%%%%%%%%%%%%%% python operator (compile engine)
_direct_implode(V) :- _computeIdx(E,python(_)), _computeIdx(E,_,V).

_direct_imploded_args_aux(E,IDX,()) :- _direct_queryArgsValues(E,python(_),_), _length(E,IDX).
_direct_imploded_args_aux(E,IDX,(IMP,L)) :- _direct_imploded_args_aux(E,IDX+1,L),
    _computeIdx(E,IDX,V),
    _direct_imploded(V,IMP).

_direct_imploded_args(E,L) :- _direct_imploded_args_aux(E,0,L).

_expression_eval_exec(E,RES) :- _computeIdx(E,python(S)),
    _direct_imploded_args(E,L),
    RES = @pythonEvalExpr(operation(python(S),L),(),ID),
    _main_solverIdentifier(ID).

_computedIdx(E,val(TYPE,V)) :- _expression_eval_exec(E,val(TYPE,V)).
_computedIdx(E,bad) :- _expression_eval_exec(E,error(KIND,MSG)).
_warning(KIND,(),(python(S),E,MSG)) :- _expression_eval_exec(E,error(KIND,MSG)), _computeIdx(E,python(S)).
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
