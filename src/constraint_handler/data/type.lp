#defined type_query/1.

%%%%%%%%%%%%%%%%% type
_type(int;float;bool;string;symbol;none;set;multimap).

%%%%%%%%%%%%%%%%% type_variable
_type_variable(type_check,X,T) :- _passed(wf_check,variable_define(LBL,X,E)), type_expression(PHASE,E,T).
_type_variable(type_check,X,T) :- _passed(wf_check,variable_domain(LBL,X,E)), type_expression(PHASE,E,T).
_type_variable(type_check,X,set) :- _passed(wf_check,set_declare(LBL,X)).
_type_variable(type_check,X,multimap) :- _passed(wf_check,multimap_declare(LBL,X)).
type_variable(X,T) :- _type_variable(PHASE,X,T).

%%%%%%%%%%%%%%%%% type_expression
_expression_query(type_check,E) :- type_query(E).
_expression_typeQuery(EXPR) :- _expression_query(wf_check,EXPR).
_expression_typeQuery(EXPR) :- type_query(EXPR).
type_expression(type_check,variable(X),T) :- _expression_typeQuery(variable(X)), _type_variable(SCOPE,X,T).
type_expression(type_check,val(T,V),T) :- _expression_typeQuery(val(T,V)).
type_expression(type_check,python(S),top) :- _expression_typeQuery(python(S)).
type_expression(type_check,E,T) :- _expression_typeQuery(E), E=operation(O,ARGS), _type_operator(O,function(TS,T)), _type_list(E,TS).
type_expression(type_check,(H,T),(TH,TT)) :- _expression_typeQuery((H,T)), type_expression(type_check,H,TH), type_expression(type_check,T,TT).


_type_listArgT(E,IDX,T) :- _expression_operationIndex(wf_check,E,IDX,ARG), type_expression(type_check,ARG,T).
_type_listAux(E,N,()) :- _expression_typeQuery(E), E=operation(O,ARGS), _expression_operationLength(wf_check,E,N).
_type_listAux(E,IDX,(T,TS)) :- _type_listAux(E,IDX+1,TS), _type_listArgT(E,IDX,T).
_type_list(E,TS) :- _type_listAux(E,0,TS).

% TODO lambdas


%%%%%%%%%%%%%%%%% type_statement
% TODO statements.

type_expressionTyped(type_check,operation(O,ARGS)) :- type_expression(type_check,operation(O,ARGS),T).
_warning(type(failed_operation),(),(O,ARGS)) :- _expression_typeQuery(operation(O,ARGS)), not type_expressionTyped(type_check,operation(O,ARGS)).


%%%%%%%%%%%%%%%%% type_operator
_type_operator(O,function(TS,T)) :- operator_declare(O,TS,T).

% This is for variadic operators
% - All valid elements get assigned their respective rank (from the declaration).
% - If the number of elements with a rank is equal to the number of arguments,
%   then all arguments were valid.
% - If all elements were valid, the result with the highest rank will be picked as the return type

operator_variadic(OP,RT) :- operator_declare_variadic(OP,T,RT,1).
_expression_sequence(type_check,TS) :- _type_list(E,TS).
_type_variadicListAux(OP,TS,N,NT,1) :- _expression_typeQuery(E), E=operation(OP,ARGS), _type_list(E,TS), _expression_sequenceLength(type_check,TS,N), operator_variadic(OP,NT).
_type_variadicListAux(OP,TS,IDX,IT,IR) :- _type_variadicListAux(OP,TS,IDX+1,NT,NR), _expression_sequenceIndex(type_check,TS,IDX,T), operator_declare_variadic(OP,T,IT,IR), IR > NR.
_type_variadicListAux(OP,TS,IDX,NT,NR) :- _type_variadicListAux(OP,TS,IDX+1,NT,NR), _expression_sequenceIndex(type_check,TS,IDX,T), operator_declare_variadic(OP,T,IT,IR), IR <= NR.
_type_operator(O,function(TS,T)) :- _type_variadicListAux(O,TS,0,T,R).

%*
_arg_rank(PHASE,OP,ARGS,IDX,RANK) :-
    _expression_index(PHASE,ARGS,IDX,ARG),
    type_expression(PHASE,ARG,T),
    operator_declare_variadic(OP,T,TRESULT,RANK).

_valid_args_count(SCOPE,OP,ARGS,COUNT) :-
    _expression_typeQuery(SCOPE,operation(OP,ARGS)),
    COUNT = #count { IDX : _arg_rank(SCOPE,OP,ARGS,IDX,RANK) }.

_max_rank(SCOPE,OP,ARGS,1) :-
    _valid_args_count(SCOPE,OP,ARGS,0).

_max_rank(SCOPE,OP,ARGS,MAXR) :-
    _valid_args_count(SCOPE,OP,ARGS,C), C > 0,
    MAXR = #max { RANK : _arg_rank(SCOPE,OP,ARGS,IDX,RANK) }.

_type_operator(SCOPE,OP,function(TS,T_RESULT)) :-
    _type_listAux(SCOPE,ARGS,N,()),
    _type_list(ARGS,TS),
    _valid_args_count(SCOPE,OP,ARGS,N),
    _max_rank(SCOPE,OP,ARGS,MAXR),
    operator_declare_variadic(OP,T,T_RESULT,MAXR).
*%
