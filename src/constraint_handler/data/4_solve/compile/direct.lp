%%%%%%%%%%%%%%%%% interface ensure/2 variable_define/3 evaluate/2
_se_assign(LBL,variable(X),E) :- _passed(compile,LBL,variable_define(X,E)).

direct_query(E)  :- _expression(compile,LBL,DECL,E).
direct_query(E)  :- _se_assign(LBL,X,E).
direct_query(SE) :- direct_query(operation(OP,ES)), not _direct_lazy(OP), SE=@pythonListElements(ES).
direct_query(SE) :- direct_query(T), SE=@pythonTupleElements(T).

_se_value(val(T,V),val(T,V)) :- direct_query(val(T,V)).
_se_value(ref(T,R),ref(T,R)) :- direct_query(ref(T,R)).
_expression_pythonEval(python(S),python(S)) :- direct_query(python(S)).
_se_value(Q,RES) :- direct_query(Q), _computedIdx(Q,RES).

_se_value(lambda(VARS,ERES),val(function,lambda(VARS,ERES))) :- direct_query(lambda(VARS,ERES)).

_se_value(variable(X),V) :- _se_assign(LBL,variable(X),E2), _se_value(E2,V).


%%%%%%%%%%%%%%%%% tuples
_direct_tupleValuesAux(E,N,()) :- _expression(compile,E), _expression_tupleLength(compile,E,N).
_direct_tupleValuesAux(E,IDX,(V,VS)) :- _direct_tupleValuesAux(E,IDX+1,VS),
    _expression_tupleIndex(compile,E,IDX,ARG), _se_value(ARG,V).
_se_value(E,TUPLE) :- _direct_tupleValuesAux(E,0,VS), TUPLE=@pythonReflect(function,(),VS).
_isTuple(compile,TUPLE) :- _direct_tupleValuesAux(E,0,VS), TUPLE=@pythonReflect(function,(),VS).

%%%%%%%%%%%%% blablablabla
_expression_dynamicTainted(bad) :- _expression(compile,bad).
_expression_dynamicTainted(EXPR) :- _expression(compile,EXPR), _expression_safeQuery(EXPR), _se_value(EXPR,bad).
_expression_dynamicTainted(EXPR) :- _expression(compile,EXPR), _expression_safeQuery(EXPR), _expression_tupleIndex(sugar,EXPR,IDX,F), _expression_dynamicTainted(F).
%_expression_dynamicTainted(EXPR) :- _expression(compile,EXPR), _expression_safeQuery(EXPR), _expression_operationIndex(sugar,EXPR,IDX,F), _expression_dynamicTainted(F), _expression_operationOperator(sugar,EXPR,OP), not _operator_recoverable(OP).
_expression_dynamicTainted(EXPR) :- _expression(compile,EXPR), _expression_safeQuery(EXPR), _expression_operationOperator(sugar,EXPR,OP), _expression_dynamicTainted(OP).
_se_value(EXPR,bad) :- _expression(compile,EXPR), _expression_safeQuery(EXPR), _expression_operationOperator(sugar,EXPR,OP), _expression_dynamicTainted(OP).
_se_value(EXPR,bad) :- _expression(compile,EXPR), _expression_safeQuery(EXPR), _expression_operationIndex(sugar,EXPR,IDX,F), _expression_dynamicTainted(F), _expression_operationOperator(sugar,EXPR,OP), not _operator_recoverable(OP).


_argument_value(operation(OP,ARGS),V) :- _expression(compile,operation(OP,ARGS)), _expression_operationIndex(compile,operation(OP,ARGS),IDX,ARG), _se_value(ARG,V).
_se_value(operation(OP,ARGS),bad) :- _argument_value(operation(OP,ARGS),bad), not _operator_recoverable(OP), not _expression_safe(operation(OP,ARGS)).

%%%%%%%%%%%%%%%%% _computedIdx operators
_direct_queryArgsValues(operation(OP,ARGS),OP,ARGS) :- direct_query(operation(OP,ARGS)), _expression_safe(operation(OP,ARGS)).
_direct_queryArgsValues(operation(OP,ARGS),OP,ARGS) :- direct_query(operation(OP,ARGS)), _operator_recoverable(OP).
_direct_queryArgsValues(operation(OP,ARGS),OP,ARGS) :- direct_query(operation(OP,ARGS)), not _operator_recoverable(OP), not _argument_value(operation(OP,ARGS),bad).
%_direct_queryArgsValues(operation(OP,ARGS),OP,ARGS) :- direct_query(operation(OP,ARGS)), not _expression_safe(operation(OP,ARGS)), not _operator_recoverable(OP), not _direct_bad_operation(OP,ARGS).
%_direct_queryArgsValues(operation(OP,ARGS),OP,ARGS) :- direct_query(operation(OP,ARGS)), not _operator_recoverable(OP), not _safe_bad(operation(OP,ARGS)). %% TODO: use static tainted instead
%_se_value(E,bad) :- _expression_dynamicTainted(E).
%_direct_queryArgsValues(operation(OP,ARGS),OP,ARGS) :- direct_query(operation(OP,ARGS)), not _direct_bad_operation(OP,ARGS).
_direct_queryArgsValues(operation(EOP,ARGS),OP,ARGS) :- direct_query(operation(EOP,ARGS)), _se_value(EOP,val(function,OP)).
_computeIdx(E,OP) :-_direct_queryArgsValues(E,OP,ARGS).
_direct_compArg(ARGS,IDX,ARG) :- _direct_queryArgsValues(E,OP,ARGS), (IDX,ARG)=@pythonEnumerateElements(ARGS).
_computeIdx(E,IDX,V) :-_direct_queryArgsValues(E,OP,ARGS), _direct_compArg(ARGS,IDX,ARG), _se_value(ARG,V).
%_computeIdx(E,IDX,V) :-_direct_queryArgsValues(E,OP,ARGS), (IDX,ARG)=@pythonEnumerateElements(ARGS), _se_value(ARG,V).
_se_value(E,VO) :- _direct_queryArgsValues(E,OP,ARGS), _computedIdx(E,VO).

%%% TODO lenght/2 is bad
%%%%%%%%%%%%%%%%% lambda application
_direct_needs_args_list(E,ARGS) :- _direct_queryArgsValues(E,lambda(LARGS,SUB),ARGS).
_length(ARGS,LEN) :- _direct_queryArgsValues(E,OP,ARGS), LEN=@pythonListLength(ARGS).
_direct_args_list_aux(E,IDX,()) :- _direct_needs_args_list(E,ARGS), _length(ARGS,IDX).
_direct_args_list_aux(E,IDX,(V,VS)) :- _direct_needs_args_list(E,ARGS), _direct_args_list_aux(E,IDX+1,VS), _computeIdx(E,IDX,V).
_direct_args_list(E,VS) :- _direct_needs_args_list(E,ARGS), _direct_args_list_aux(E,0,VS).

_lambda_aux(E,RED) :- _computeIdx(E,lambda(VARS,ERES)),
    _direct_args_list(E,ARGS),
    valid(RED)=@pythonBetaReduction(ERES,VARS,ARGS).

direct_query(RED) :- _lambda_aux(E,RED).
_computedIdx(E,VO) :- _lambda_aux(E,RED), _se_value(RED,VO).

%%%%%%%%%%%%%%%%% python operator
_direct_implode(V) :- _computeIdx(E,python(STR)), _computeIdx(E,IDX,V).
_direct_imploded_args_aux(E,IDX,()) :- _direct_queryArgsValues(E,python(STR),ARGS), _length(ARGS,IDX).
_direct_imploded_args_aux(E,IDX,(IMP,L)) :- _direct_imploded_args_aux(E,IDX+1,L), _computeIdx(E,IDX,V),
    _direct_imploded(V,IMP).

_expression_pythonEval(E,operation(python(S),L)) :- _computeIdx(E,python(S)), _direct_imploded_args_aux(E,0,L).

_expression_eval_exec(Q,RES) :- _expression_pythonEval(Q,E), RES=@pythonEvalExpr(E,(),ID), _main_solverIdentifiers(ID).
_computedIdx(E,val(TYPE,V)) :- _expression_eval_exec(E,valid(val(TYPE,V))).
_computedIdx(E,bad) :- _expression_eval_exec(E,error(KIND,MSG)).
_warning(KIND,(),(python,E,MSG)) :- _expression_eval_exec(E,error(KIND,MSG)).


_set_declare(_internal,E) :- _expression_eval_exec(E,valid(set(S))).
_set_assign(_internal,E,VAL) :- _expression_eval_exec(E,valid(set(S))), VAL=@pythonListElements(S).


%%%%%%%%%%%%%%%%% pythonExtract operator
_direct_implode(V) :- _computeIdx(E,pythonExtract(PSTMT,PEXPR)), _computeIdx(E,IDX,V).
_direct_imploded_args_aux(E,IDX,()) :- _direct_queryArgsValues(E,pythonExtract(PSTMT,PEXPR),ARGS), _length(ARGS,IDX).
_direct_imploded_args_aux(E,IDX,(IMP,L)) :- _direct_imploded_args_aux(E,IDX+1,L), _computeIdx(E,IDX,V),
    _direct_imploded(V,IMP).
_expression_pythonEval(E,operation(pythonExtract(PSTMT,PEXPR),L)) :- _computeIdx(E,pythonExtract(PSTMT,PEXPR)), _direct_imploded_args_aux(E,0,L).

%%%%%%%%%%%%%%%%% bad
%_direct_bad_operation(OP,ARGS) :- direct_query(operation(OP,ARGS)), _se_value(ARG,bad), ARG=@pythonListElements(ARGS), not _expression_safe(operation(OP,ARGS)), not _operator_recoverable(OP).
%_direct_bad_operation(OP,ARGS) :- direct_query(operation(OP,ARGS)), _se_value(ARG,bad), ARG=@pythonListElements(ARGS), not _operator_recoverable(OP).
%_direct_bad_operation(OP,ARGS) :- direct_query(operation(OP,ARGS)), _se_value(OP,bad).
%_se_value(operation(OP,ARGS),bad) :- _direct_bad_operation(OP,ARGS).
%_se_value(bad,bad) :- direct_query(bad).
_se_value(bad,bad).
%_direct_imploded(bad,bad).

%%%%%%%%%%%%%%%%% implode
_direct_imploded(val(T,V),val(T,V)) :- _direct_implode(val(T,V)), representation(T,extensional).

_direct_imploded(variable(X),V) :- _direct_implode(variable(X)), _se_value(variable(X),V).
_direct_implode(V) :- _direct_implode(variable(X)), _se_value(variable(X),V).
_direct_imploded(variable(X),W) :- _direct_implode(variable(X)), _se_value(variable(X),V), _direct_imploded(V,W).

_isTuple(compile,E) :- _direct_implode(E), true=@pythonIsTuple(E).
_isTuple(compile,E,N,ARGS) :- _direct_implode(E), (function,(),N,ARGS)=@pythonReify(E).
_direct_implode(X) :- _direct_implode(E), _expression_tupleIndex(compile,E,IDX,X).
_direct_implodeTupleAux(E,N,()) :- _direct_implode(E), _expression_tupleLength(compile,E,N).
_direct_implodeTupleAux(E,IDX,(V,L)) :- _direct_implodeTupleAux(E,IDX+1,L), _expression_tupleIndex(compile,E,IDX,X), _direct_imploded(X,V).
_direct_imploded(E,TUPLE) :- _direct_implodeTupleAux(E,0,L), TUPLE=@pythonReflect(function,(),L).

engine(_internal,compile).
