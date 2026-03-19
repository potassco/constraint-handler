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

_expr_id(E_ID,E) :- direct_query(E), E_ID=@pythonId(E).

_se_value(E,E) :- direct_query(E), E=val(_,_).
_se_value(E,E) :- direct_query(E), E=ref(_,_).


_se_value(E,val(function,E)) :- direct_query(E), E=lambda(VARS,ERES).

_se_value(E,V) :- direct_query(E), E=variable(X), _se_assign(NAME,E,E2), _se_value(E2,V), usc_active(NAME).

_se_value_id(E_ID,V) :- _se_value(E,V), E_ID=@pythonId(E).





%%%%%%%%%%%%%%%%% _computedIdx operators
_direct_queryArgsValues(E,OP,ARGS) :- direct_query(E), E=operation(OP,ARGS). % decl operator
_direct_queryArgsValues(E,OP,ARGS) :- direct_query(E), E=operation(EOP,ARGS), _se_value(EOP,val(function,OP)).
_direct_queryArgsValues_id(E_ID,OP,ARGS) :- _expr_id(E_ID,E), _direct_queryArgsValues(E,OP,ARGS).
_computeIdx_id(E_ID,OP) :- _direct_queryArgsValues_id(E_ID,OP,ARGS).
_direct_compArg(ARGS,IDX,ARG) :- _direct_queryArgsValues(E,OP,ARGS), (IDX,ARG)=@pythonEnumerateElements(ARGS).
_computeIdx_id(E_ID,IDX,V) :- _direct_queryArgsValues_id(E_ID,OP,ARGS), _direct_compArg(ARGS,IDX,ARG), ARG_ID=@pythonId(ARG), _se_value_id(ARG_ID,V).
_computeIdx(E,OP) :- _expr_id(E_ID,E), _computeIdx_id(E_ID,OP).
_computeIdx(E,IDX,V) :- _expr_id(E_ID,E), _computeIdx_id(E_ID,IDX,V).
_computedIdx_id(E_ID,VO) :- _expr_id(E_ID,E), _computedIdx(E,VO).
_computedIdx(E,VO) :- _expr_id(E_ID,E), _computedIdx_id(E_ID,VO).
_se_value(E,VO) :- _expr_id(E_ID,E), _computedIdx_id(E_ID,VO).

%%%%%%%%%%%%%%%%% argument-list helpers (compile engine)
% Only needed for lambda application. Guarding this prevents grounding
% all argument combinations for every operation.
_direct_needs_args_list_id(E_ID) :- _direct_queryArgsValues_id(E_ID,OP,_), OP=lambda(_,_).
_direct_needs_args_list(E) :- _expr_id(E_ID,E), _direct_needs_args_list_id(E_ID).

_direct_args_list_aux_id(E_ID,IDX,()) :- _direct_needs_args_list_id(E_ID), _direct_queryArgsValues_id(E_ID,_,ARGS), IDX=@pythonListLength(ARGS).
_direct_args_list_aux_id(E_ID,IDX,(V,VS)) :- _direct_needs_args_list_id(E_ID), _direct_args_list_aux_id(E_ID,IDX+1,VS), _computeIdx_id(E_ID,IDX,V).
_direct_args_list_aux(E,IDX,VS) :- _expr_id(E_ID,E), _direct_args_list_aux_id(E_ID,IDX,VS).
_direct_args_list_id(E_ID,VS) :- _direct_needs_args_list_id(E_ID), _direct_args_list_aux_id(E_ID,0,VS).
_direct_args_list(E,VS) :- _expr_id(E_ID,E), _direct_args_list_id(E_ID,VS).

%%%%%%%%%%%%%%%%% lambda application
_lambda_aux_id(E_ID,RED) :- _computeIdx_id(E_ID,LAMB),
    LAMB=lambda(VARS,ERES),
    _direct_args_list_id(E_ID,ARGS),
    RED=@pythonBetaReduction(ERES,VARS,ARGS).
_lambda_aux(E,RED) :- _expr_id(E_ID,E), _lambda_aux_id(E_ID,RED).

direct_query(RED) :- _lambda_aux_id(E_ID,RED).
_computedIdx_id(E_ID,VO) :- _lambda_aux_id(E_ID,RED), _se_value(RED,VO).

%%%%%%%%%%%%%%%%% python operator (compile engine)
_direct_implode_id(E_ID,V) :- _computeIdx_id(E_ID,python(_)), _computeIdx_id(E_ID,_,V).
_direct_implode(V) :- _expr_id(E_ID,E), _direct_implode_id(E_ID,V).

_direct_imploded_args_aux_id(E_ID,IDX,()) :- _direct_queryArgsValues_id(E_ID,python(_),ARGS), IDX=@pythonListLength(ARGS).
_direct_imploded_args_aux_id(E_ID,IDX,(IMP,L)) :- _direct_imploded_args_aux_id(E_ID,IDX+1,L),
    _computeIdx_id(E_ID,IDX,V),
    _direct_imploded(V,IMP).
_direct_imploded_args_aux(E,IDX,L) :- _expr_id(E_ID,E), _direct_imploded_args_aux_id(E_ID,IDX,L).

_direct_imploded_args_id(E_ID,L) :- _direct_imploded_args_aux_id(E_ID,0,L).
_direct_imploded_args(E,L) :- _expr_id(E_ID,E), _direct_imploded_args_id(E_ID,L).

_expression_eval_exec_id(E_ID,RES) :- _computeIdx_id(E_ID,python(S)),
    _direct_imploded_args_id(E_ID,L),
    RES = @pythonEvalExpr(operation(python(S),L),(),ID),
    _main_solverIdentifier(ID).
_expression_eval_exec(E,RES) :- _expr_id(E_ID,E), _expression_eval_exec_id(E_ID,RES).

_computedIdx_id(E_ID,val(TYPE,V)) :- _expression_eval_exec_id(E_ID,val(TYPE,V)).
_computedIdx_id(E_ID,bad) :- _expression_eval_exec_id(E_ID,error(KIND,MSG)).
_warning(KIND,(),(python(S),E,MSG)) :- _expr_id(E_ID,E), _expression_eval_exec_id(E_ID,error(KIND,MSG)), _computeIdx_id(E_ID,python(S)).
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
