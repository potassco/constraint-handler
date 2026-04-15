#defined type_query/1.

%%%%%%%%%%%%%%%%% type
_type(int;float;bool;string;symbol;none;set;multimap).

%%%%%%%%%%%%%%%%% type_variable
type_variable((),X,T) :- _passed(sugar,variable_define(LBL,X,E)), type_expression((),E,T).
type_variable((),X,T) :- _passed(sugar,variable_domain(LBL,X,E)), type_expression((),E,T).
type_variable((),X,set) :- set_declare(LBL,X).
type_variable((),X,multimap) :- multimap_declare(LBL,X).

%%%%%%%%%%%%%%%%% type_expression
_expression_query((),E) :- type_query(E).
type_expression(SCOPE,variable(X),T) :- _expression_query(SCOPE,variable(X)), type_variable(SCOPE,X,T).
type_expression(SCOPE,val(T,V),T) :- _expression_query(SCOPE,val(T,V)).
type_expression(SCOPE,python(S),top) :- _expression_query(SCOPE,python(S)).
type_expression(SCOPE,operation(O,ARGS),T) :- _expression_query(SCOPE,operation(O,ARGS)), _type_operator(SCOPE,O,function(TS,T)), _type_list(SCOPE,ARGS,TS).
type_expression(SCOPE,(H,T),(TH,TT)) :- _expression_query(SCOPE,(H,T)), type_expression(SCOPE,H,TH), type_expression(SCOPE,T,TT).

_length(ARGS,N) :- _expression_query(SCOPE,operation(O,ARGS)), N=@pythonListLength(ARGS).
_type_listArg(SCOPE,ARGS,IDX,ARG) :- _expression_query(SCOPE,operation(O,ARGS)), (IDX,ARG)=@pythonEnumerateElements(ARGS).
_type_listAux(SCOPE,ARGS,N,()) :- _expression_query(SCOPE,operation(O,ARGS)), _length(ARGS,N).
_type_listAux(SCOPE,ARGS,N-1,(T,TS)) :- _type_listAux(SCOPE,ARGS,N,TS), _type_listArg(SCOPE,ARGS,N-1,ARG), type_expression(SCOPE,ARG,T).

_type_list(SCOPE,ARGS,TS) :- _type_listAux(SCOPE,ARGS,0,TS).

% TODO lambdas


%%%%%%%%%%%%%%%%% type_statement
% TODO statements.

type_expressionTyped(SCOPE,operation(O,ARGS)) :- type_expression(SCOPE,operation(O,ARGS),T).
_warning(type(failed_operation),(),(SCOPE,O,ARGS)) :- _expression_query(SCOPE,operation(O,ARGS)), not type_expressionTyped(SCOPE,operation(O,ARGS)).


%%%%%%%%%%%%%%%%% type_operator
_type_operator((),O,function(TS,T)) :- operator_declare(O,TS,T).

% This is for variadic operators
% - All valid elements get assigned their respective rank (from the declaration).
% - If the number of elements with a rank is equal to the number of arguments,
%   then all arguments were valid.
% - If all elements were valid, the result with the highest rank will be picked as the return type
_arg_rank(SCOPE,OP,ARGS,IDX,RANK) :-
    _type_listArg(SCOPE,ARGS,IDX,ARG),
    type_expression(SCOPE,ARG,T),
    operator_declare_variadic(OP,T,TRESULT,RANK).

_valid_args_count(SCOPE,OP,ARGS,COUNT) :-
    _expression_query(SCOPE,operation(OP,ARGS)),
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
