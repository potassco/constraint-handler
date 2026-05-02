%%%%%%%%%%%%%%%%% interface ensure/2 variable_define/3 evaluate/2
_expression_valueQuery(LBL,E) :- _passed(sugar,ensure(LBL,E)), engine(LBL,(compile;ground)).
_expression_valueQuery(LBL,operation(OP,ARGS)) :- _passed(sugar,evaluate(LBL,OP,ARGS)), engine(LBL,(compile;ground)).
_expression_valueQuery(LBL,E) :- _passed(sugar,variable_define(LBL,X,E)), engine(LBL,(compile;ground)).
_expression_valueQuery(LBL,E) :- _passed(sugar,variable_domain(LBL,X,E)), engine(LBL,(compile;ground)).
_se_assign(LBL,variable(X),E) :- _passed(sugar,variable_define(LBL,X,E)), engine(LBL,compile).

:- _passed(sugar,ensure(CNAME,E)), engine(CNAME,(compile;ground)), not _se_value(E,val(bool,true)), not _se_value(E,bad).
evaluated(OP,ARGS,V) :- _passed(sugar,evaluate(LBL,OP,ARGS)), _se_value(operation(OP,ARGS),V).


direct_query(E)  :- _expression_valueQuery(LBL,E), engine(LBL,compile).
direct_query(E)  :- _se_assign(NAME,X,E).
direct_query(X)  :- _se_assign(NAME,X,E).
direct_query(SE) :- direct_query(operation(OP,ES)), not _direct_lazy(OP), SE=@pythonListElements(ES).
direct_query(SE) :- direct_query(T), SE=@pythonTupleElements(T).

_se_value(val(T,V),val(T,V)) :- direct_query(val(T,V)).
_se_value(ref(T,R),ref(T,R)) :- direct_query(ref(T,R)).
_expression_pythonEval(python(S),python(S)) :- direct_query(python(S)).
_se_value(Q,RES) :- direct_query(Q), _computedIdx(Q,RES).

_se_value(lambda(VARS,ERES),val(function,lambda(VARS,ERES))) :- direct_query(lambda(VARS,ERES)).

_se_value(variable(X),V) :- direct_query(variable(X)), _se_assign(NAME,variable(X),E2), _se_value(E2,V).


%%%%%%%%%%%%%%%%% tuples
_direct_tupleValuesAux(E,ARGS,N,()) :- direct_query(E), _expression_isTuple(E,N,ARGS).
_direct_tupleValuesAux(E,ARGS,IDX,(V,VS)) :- _direct_tupleValuesAux(E,ARGS,IDX+1,VS),
    _expression_index(ARGS,IDX,ARG), _se_value(ARG,V).
_se_value(E,TUPLE) :- _direct_tupleValuesAux(E,ARGS,0,VS), TUPLE=@pythonReflect(function,(),VS).

%%%%%%%%%%%%%%%%% _computedIdx operators
_direct_queryArgsValues(operation(OP,ARGS),OP,ARGS) :- direct_query(operation(OP,ARGS)), _expression_safe((),operation(OP,ARGS)).
_direct_queryArgsValues(operation(OP,ARGS),OP,ARGS) :- direct_query(operation(OP,ARGS)), _operator_recoverable(OP).
_direct_queryArgsValues(operation(OP,ARGS),OP,ARGS) :- direct_query(operation(OP,ARGS)), not _expression_safe((),operation(OP,ARGS)), not _operator_recoverable(OP), not _direct_bad_operation(OP,ARGS).
%_direct_queryArgsValues(operation(OP,ARGS),OP,ARGS) :- direct_query(operation(OP,ARGS)), not _direct_bad_operation(OP,ARGS).
_direct_queryArgsValues(operation(EOP,ARGS),OP,ARGS) :- direct_query(operation(EOP,ARGS)), _se_value(EOP,val(function,OP)).
_computeIdx(E,OP) :-_direct_queryArgsValues(E,OP,ARGS).
_direct_compArg(ARGS,IDX,ARG) :- _direct_queryArgsValues(E,OP,ARGS), (IDX,ARG)=@pythonEnumerateElements(ARGS).
_computeIdx(E,IDX,V) :-_direct_queryArgsValues(E,OP,ARGS), _direct_compArg(ARGS,IDX,ARG), _se_value(ARG,V).
_se_value(E,VO) :- _direct_queryArgsValues(E,OP,ARGS), _computedIdx(E,VO).


%%%%%%%%%%%%%%%%% lambda application
_direct_needs_args_list(E,ARGS) :- _direct_queryArgsValues(E,lambda(LARGS,SUB),ARGS).
_length(ARGS,LEN) :- _direct_queryArgsValues(E,OP,ARGS), LEN=@pythonListLength(ARGS).
_direct_args_list_aux(E,IDX,()) :- _direct_needs_args_list(E,ARGS), _length(ARGS,IDX).
_direct_args_list_aux(E,IDX,(V,VS)) :- _direct_needs_args_list(E,ARGS), _direct_args_list_aux(E,IDX+1,VS), _computeIdx(E,IDX,V).
_direct_args_list(E,VS) :- _direct_needs_args_list(E,ARGS), _direct_args_list_aux(E,0,VS).

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

%%%%%%%%%%%%%%%%% bad
_direct_bad_operation(OP,ARGS) :- direct_query(operation(OP,ARGS)), _se_value(ARG,bad), ARG=@pythonListElements(ARGS), not _expression_safe((),operation(OP,ARGS)), not _operator_recoverable(OP).
%_direct_bad_operation(OP,ARGS) :- direct_query(operation(OP,ARGS)), _se_value(ARG,bad), ARG=@pythonListElements(ARGS), not _operator_recoverable(OP).
_direct_bad_operation(OP,ARGS) :- direct_query(operation(OP,ARGS)), _se_value(OP,bad).
_se_value(operation(OP,ARGS),bad) :- _direct_bad_operation(OP,ARGS).
_se_value(bad,bad) :- direct_query(bad).

%%%%%%%%%%%%%%%%% implode
_direct_imploded(val(T,V),val(T,V)) :- _direct_implode(val(T,V)), representation(T,extensional).

_direct_imploded(variable(X),V) :- _direct_implode(variable(X)), _se_value(variable(X),V).

engine(_internal,compile).
