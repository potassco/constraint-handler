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
_expression_typeQuery(type_check,EXPR) :- _expression_query(wf_check,EXPR).
_expression_typeQuery(type_check,EXPR) :- type_query(EXPR).
type_expression(SCOPE,variable(X),T) :- _expression_typeQuery(SCOPE,variable(X)), _type_variable(SCOPE,X,T).
type_expression(SCOPE,val(T,V),T) :- _expression_typeQuery(SCOPE,val(T,V)).
type_expression(SCOPE,python(S),top) :- _expression_typeQuery(SCOPE,python(S)).
type_expression(SCOPE,operation(O,ARGS),T) :- _expression_typeQuery(SCOPE,operation(O,ARGS)), _type_operator(SCOPE,O,function(TS,T)), _type_list(SCOPE,ARGS,TS).
type_expression(SCOPE,(H,T),(TH,TT)) :- _expression_typeQuery(SCOPE,(H,T)), type_expression(SCOPE,H,TH), type_expression(SCOPE,T,TT).

_expression_sequenceHelper(PHASE,ARGS) :- _expression_typeQuery(PHASE,operation(O,ARGS)).
_expression_sequenceHelper(PHASE,EXPR) :- _expression_typeQuery(PHASE,EXPR).

_type_listArgT(SCOPE,ARGS,IDX,T) :- _expression_index(SCOPE,ARGS,IDX,ARG), type_expression(SCOPE,ARG,T).
_type_listAux(SCOPE,ARGS,N,()) :- _expression_typeQuery(SCOPE,operation(O,ARGS)), _length(SCOPE,ARGS,N).
_type_listAux(SCOPE,ARGS,IDX,(T,TS)) :- _type_listAux(SCOPE,ARGS,IDX+1,TS), _type_listArgT(SCOPE,ARGS,IDX,T).
_type_list(SCOPE,ARGS,TS) :- _type_listAux(SCOPE,ARGS,0,TS).

% TODO lambdas


%%%%%%%%%%%%%%%%% type_statement
% TODO statements.

type_expressionTyped(SCOPE,operation(O,ARGS)) :- type_expression(SCOPE,operation(O,ARGS),T).
_warning(type(failed_operation),(),(O,ARGS)) :- _expression_typeQuery(SCOPE,operation(O,ARGS)), not type_expressionTyped(SCOPE,operation(O,ARGS)).


%%%%%%%%%%%%%%%%% type_operator
_type_operator(type_check,O,function(TS,T)) :- operator_declare(O,TS,T).

% This is for variadic operators
% - All valid elements get assigned their respective rank (from the declaration).
% - If the number of elements with a rank is equal to the number of arguments,
%   then all arguments were valid.
% - If all elements were valid, the result with the highest rank will be picked as the return type

%_expression_sequenceHelper(PHASE,TS) :- _type_list(PHASE,ARGS,TS).
_expression_sequenceHelper(type_check,TS) :- _type_list(type_check,ARGS,TS).

operator_variadic(OP,RT) :- operator_declare_variadic(OP,T,RT,1).
_type_variadicListAux(PHASE,OP,TS,N,NT,1) :- _expression_typeQuery(PHASE,operation(OP,ARGS)), _type_list(PHASE,ARGS,TS), _length(PHASE,ARGS,N), operator_variadic(OP,NT).
_type_variadicListAux(PHASE,OP,TS,IDX,IT,IR) :- _type_variadicListAux(PHASE,OP,TS,IDX+1,NT,NR), _expression_index(PHASE,TS,IDX,T), operator_declare_variadic(OP,T,IT,IR), IR > NR.
_type_variadicListAux(PHASE,OP,TS,IDX,NT,NR) :- _type_variadicListAux(PHASE,OP,TS,IDX+1,NT,NR), _expression_index(PHASE,TS,IDX,T), operator_declare_variadic(OP,T,IT,IR), IR <= NR.
_type_operator(PHASE,O,function(TS,T)) :- _type_variadicListAux(PHASE,O,TS,0,T,R).
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
    _type_list(SCOPE,ARGS,TS),
    _valid_args_count(SCOPE,OP,ARGS,N),
    _max_rank(SCOPE,OP,ARGS,MAXR),
    operator_declare_variadic(OP,T,T_RESULT,MAXR).
*%
