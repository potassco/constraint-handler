_main(type_check).

#defined type_query/1.

%%%%%%%%%%%%%%%%% type
_type(int;float;bool;string;symbol;none;set;multimap).

%%%%%%%%%%%%%%%%% type_variable
_type_variable(X,T) :- _main(type_check), _passed(sugar,variable_define(LBL,X,E)), type_expression(E,T).
_type_variable(X,T) :- _main(type_check), _passed(sugar,variable_domain(LBL,X,E)), type_expression(E,T).
_type_variable(X,set) :- _main(type_check), _passed(sugar,variable_declare(LBL,X,set)).
_type_variable(X,multimap) :- _main(type_check), _passed(sugar,variable_declare(LBL,X,multimap)).
type_variable(X,T) :- _type_variable(X,T).

%%%%%%%%%%%%%%%%% type_expression
_expression_typeQuery(EXPR) :- _main(type_check), _expression(sugar,EXPR).
_expression_typeQuery(EXPR) :- _main(type_check), type_query(EXPR).
type_expression(variable(X),T) :- _expression_typeQuery(variable(X)), _type_variable(X,T).
type_expression(val(T,V),T) :- _expression_typeQuery(val(T,V)).
type_expression(python(S),top) :- _expression_typeQuery(python(S)).
type_expression(operation(O,ARGS),T) :- _expression_typeQuery(operation(O,ARGS)), _type_operator(O,function(TS,T)), _type_list(operation(O,ARGS),TS).
type_expression((H,T),(TH,TT)) :- _expression_typeQuery((H,T)), type_expression(H,TH), type_expression(T,TT). %TODO general tuples


_type_listArgT(E,IDX,T) :- _expression_operationIndex(sugar,E,IDX,ARG), type_expression(ARG,T).
_type_listAux(E,N,()) :- _expression_typeQuery(E), E=operation(O,ARGS), _expression_operationLength(sugar,E,N).
_type_listAux(E,IDX,(T,TS)) :- _type_listAux(E,IDX+1,TS), _type_listArgT(E,IDX,T).
_type_list(E,TS) :- _type_listAux(E,0,TS).

% TODO lambdas


%%%%%%%%%%%%%%%%% type_statement
% TODO statements.

type_expressionTyped(operation(O,ARGS)) :- type_expression(operation(O,ARGS),T).
_warning(type(failed_operation),(),(O,ARGS)) :- _expression_typeQuery(operation(O,ARGS)), not type_expressionTyped(operation(O,ARGS)).


%%%%%%%%%%%%%%%%% type_operator
_type_operator(O,function(TS,T)) :- _main(type_check), operator_declare(O,TS,T).

% This is for variadic operators
% - All valid elements get assigned their respective rank (from the declaration).
% - If the number of elements with a rank is equal to the number of arguments,
%   then all arguments were valid.
% - If all elements were valid, the result with the highest rank will be picked as the return type

_expression_sequenceLength(type_check,E,N) :- _expression_sequence(type_check,E), N=@pythonListLength(E).
_expression_sequenceIndex(type_check,E,IDX,X) :- _expression_sequence(type_check,E), (IDX,X)=@pythonEnumerateElements(E).



operator_variadic(OP,RT) :- operator_declare_variadic(OP,T,RT,1).
_expression_sequence(type_check,TS) :- _type_list(E,TS).
_type_variadicListAux(OP,TS,N,NT,1) :- _expression_typeQuery(E), E=operation(OP,ARGS), _type_list(E,TS), _expression_sequenceLength(type_check,TS,N), operator_variadic(OP,NT).
_type_variadicListAux(OP,TS,IDX,IT,IR) :- _type_variadicListAux(OP,TS,IDX+1,NT,NR), _expression_sequenceIndex(type_check,TS,IDX,T), operator_declare_variadic(OP,T,IT,IR), IR > NR.
_type_variadicListAux(OP,TS,IDX,NT,NR) :- _type_variadicListAux(OP,TS,IDX+1,NT,NR), _expression_sequenceIndex(type_check,TS,IDX,T), operator_declare_variadic(OP,T,IT,IR), IR <= NR.
_type_operator(O,function(TS,T)) :- _type_variadicListAux(O,TS,0,T,R).
