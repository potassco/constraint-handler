%%%%%%%%%%%%%%%%% interface ensure/2 assign/3 evaluate/2
_se_ensure(CNAME,E) :- _passed(sugar,ensure(CNAME,E)), engine(CNAME,compile).
_se_assign(CNAME,variable(X),E) :- assign(CNAME,X,E), engine(CNAME,compile).
_se_evaluate(CNAME,OP,ARGS) :- _passed(sugar,evaluate(CNAME,OP,ARGS)), engine(CNAME,compile).

evaluated(OP,ARGS,V) :- _se_evaluate(CNAME,OP,ARGS), _se_value(operation(OP,ARGS),V).


direct_query(E)  :- _se_ensure(NAME,E).
direct_query(E)  :- _se_assign(NAME,X,E).
direct_query(X)  :- _se_assign(NAME,X,E).
direct_query(operation(OP,ARGS))  :- _se_evaluate(CNAME,OP,ARGS).
direct_query(SE) :- direct_query(operation(OP,ES)), not _direct_lazy(OP), SE=@pythonListElements(ES).

_se_value(val(T,V),val(T,V)) :- direct_query(val(T,V)).
_se_value(ref(T,R),ref(T,R)) :- direct_query(ref(T,R)).

_se_value(lambda(VARS,ERES),val(function,lambda(VARS,ERES))) :- direct_query(lambda(VARS,ERES)).

_se_value(variable(X),V) :- direct_query(variable(X)), _se_assign(NAME,variable(X),E2), _se_value(E2,V), usc_active(NAME).



%%%%%%%%%%%%%%%%% _computedIdx operators
_direct_queryArgsValues(operation(OP,ARGS),OP,ARGS) :- direct_query(operation(OP,ARGS)). % decl operator
_direct_queryArgsValues(operation(EOP,ARGS),OP,ARGS) :- direct_query(operation(EOP,ARGS)), _se_value(EOP,val(function,OP)).
_computeIdx(E,OP) :-_direct_queryArgsValues(E,OP,ARGS).
_direct_compArg(ARGS,IDX,ARG) :- _direct_queryArgsValues(E,OP,ARGS), (IDX,ARG)=@pythonEnumerateElements(ARGS).
_computeIdx(E,IDX,V) :-_direct_queryArgsValues(E,OP,ARGS), _direct_compArg(ARGS,IDX,ARG), _se_value(ARG,V).
_se_value(E,VO) :- _direct_queryArgsValues(E,OP,ARGS), _computedIdx(E,VO).


%%%%%%%%%%%%%%%%% lambda application
_direct_needs_args_list(E) :- _direct_queryArgsValues(E,lambda(LARGS,SUB),ARGS).
_length(ARGS,LEN) :- _direct_queryArgsValues(E,OP,ARGS), LEN=@pythonListLength(ARGS).
_direct_args_list_aux(E,IDX,()) :- _direct_needs_args_list(E), _length(ARGS,IDX).
_direct_args_list_aux(E,IDX,(V,VS)) :- _direct_needs_args_list(E), _direct_args_list_aux(E,IDX+1,VS), _computeIdx(E,IDX,V).
_direct_args_list(E,VS) :- _direct_needs_args_list(E), _direct_args_list_aux(E,0,VS).

_lambda_aux(E,RED) :- _computeIdx(E,lambda(VARS,ERES)),
    _direct_args_list(E,ARGS),
    RED=@pythonBetaReduction(ERES,VARS,ARGS).

direct_query(RED) :- _lambda_aux(E,RED).
_computedIdx(E,VO) :- _lambda_aux(E,RED), _se_value(RED,VO).

%%%%%%%%%%%%%%%%% python operator
_direct_implode(V) :- _computeIdx(E,python(STR)), _computeIdx(E,IDX,V).
_direct_imploded_args_aux(E,IDX,()) :- _direct_queryArgsValues(E,python(STR),ARGS), _length(ARGS,IDX).
_direct_imploded_args_aux(E,IDX,(IMP,L)) :- _direct_imploded_args_aux(E,IDX+1,L), _computeIdx(E,IDX,V),
    _direct_imploded(V,IMP).
_expression_pythonEval(E,operation(python(S),L)) :- _computeIdx(E,python(S)), _direct_imploded_args_aux(E,0,L).

_expression_eval_exec(Q,RES) :- _expression_pythonEval(Q,E), RES=@pythonEvalExpr(E,(),ID), _main_solverIdentifier(ID).
_computedIdx(E,val(TYPE,V)) :- _expression_eval_exec(E,val(TYPE,V)).
_computedIdx(E,bad) :- _expression_eval_exec(E,error(KIND,MSG)).
_warning(KIND,(),(python,E,MSG)) :- _expression_eval_exec(E,error(KIND,MSG)).

%%%%%%%%%%%%%%%%% function definitions
assign(CNAME,X,lambda(VARS,EXPR)) :- define(CNAME,X,VARS,EXPR).
%direct_query(ER) :- direct_query(E), beta_reduction(E,ER).
%_se_value(E,T,V) :- direct_query(E), beta_reduction(E,ER), _se_value(ER,T,V).

%%%%%%%%%%%%%%%%% bad
_se_value(operation(OP,ARGS),bad) :- direct_query(operation(OP,ARGS)), _se_value(ARG,bad), ARG=@pythonListElements(ARGS), not _operator_recoverable(OP).
_se_value(operation(OP,ARGS),bad) :- direct_query(operation(OP,ARGS)), _se_value(OP,bad).
_se_value(bad,bad) :- direct_query(bad).

%%%%%%%%%%%%%%%%% implode
_direct_imploded(val(T,V),val(T,V)) :- _direct_implode(val(T,V)), representation(T,extensional).

_direct_imploded(variable(X),V) :- _direct_implode(variable(X)), _se_value(variable(X),V).

engine(_internal,compile).
#external usc_relax(NAME) : engine(NAME,E).
{ usc_active(NAME) } :- engine(NAME,E).
usc_active(NAME) :- engine(NAME,E), not usc_relax(NAME).
:- _se_ensure(NAME,E), not _se_value(E,val(bool,true)), not _se_value(E,bad), usc_active(NAME).
