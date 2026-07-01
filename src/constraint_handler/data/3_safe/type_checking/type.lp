#defined type_query/1.

%%%%%%%%%%%%%%%%% type
_type(bot;int;float;bool;string;symbol;none;set;multimap).

%%%%%%%%%%%%%%%%% expression
_expression(type_check,operation(pythonExtract("",S),())) :- _expression(type_check,python(S)).
_expression(type_check,EXPR) :- _phase_active(type_check), _expression(sugar,EXPR).
_expression(type_check,EXPR) :- _phase_active(type_check), type_query(EXPR).
_expression(type_check,variable(X)) :- _phase_active(type_check), _variable_exists(sugar,X).

%%%%%%%%%%%%%%%%% type_variable
_type_variable(X,T) :- _phase_active(type_check), _passed(sugar,LBL,variable_define(X,E)), _type_expression(E,T).
_type_variable(X,T) :- _phase_active(type_check), _passed(sugar,LBL,variable_domain(X,E)), _type_expression(E,T).
_type_variable(X,set) :- _phase_active(type_check), _passed(sugar,LBL,variable_declare(X,set)).
_type_variable(X,multimap) :- _phase_active(type_check), _passed(sugar,LBL,variable_declare(X,multimap)).
type_variable(X,T) :- _type_variable(X,T).

%%%%%%%%%%%%%%%%% _type_expression
_type_expression(bad,bot) :- _phase_active(type_check).
_type_expression(variable(X),T) :- _expression(type_check,variable(X)), _type_variable(X,T).
_type_expression(val(T,V),T) :- _expression(type_check,val(T,V)).
_type_expression(python(S),T) :- _expression(type_check,python(S)), _type_expression(operation(pythonExtract("",S),()),T).
_type_expression(operation(O,ARGS),T) :- _expression(type_check,operation(O,ARGS)), operator_declare(O,TS,T), _type_expressions(ARGS,TS).
_type_expression(operation(O,ARGS),bot) :- _expression(type_check,operation(O,ARGS)), not _operator_variadic(O), _type_expressions(ARGS,TS), #false: operator_declare(O,TS,T).
_type_expression(operation(O,ARGS),bot) :- _expression(type_check,operation(O,ARGS)), _operator_variadic(O), _expression_operationIndex(type_check,operation(O,ARGS),IDX,ARG), _type_expression(ARG,T), not _operator_variadicAccepts(O,T).
_type_expression(operation(O,ARGS),top) :- _expression(type_check,operation(O,ARGS)), _type_expression(O,top).
_type_expression(E,top) :- _expression(type_check,E), _expression_operationIndex(type_check,E,IDX,ARG), _type_expression(ARG,top).
_type_expression((H,T),(TH,TT)) :- _expression(type_check,(H,T)), _type_expression(H,TH), _type_expression(T,TT). %TODO general tuples

_expression_sequence(type_check,ARGS) :- _expression(type_check,operation(OP,ARGS)).

_type_expressionsArgT(S,IDX,T) :- _expression_sequenceIndex(type_check,S,IDX,ARG), _type_expression(ARG,T).
_type_expressionsAux(S,N,()) :- _expression_sequenceLength(type_check,S,N).
_type_expressionsAux(S,IDX,(T,TS)) :- _type_expressionsAux(S,IDX+1,TS), _type_expressionsArgT(S,IDX,T).
_type_expressions(S,TS) :- _type_expressionsAux(S,0,TS).

% TODO lambdas
_type_expression(lambda(ARGS,E),top) :- _expression(type_check,lambda(ARGS,E)).



%%%%%%%%%%%%%%%%% variadic operators
% - All valid elements get assigned their respective rank (from the declaration).
% - If the number of elements with a rank is equal to the number of arguments,
%   then all arguments were valid.
% - If all elements were valid, the result with the highest rank will be picked as the return type

_expression_sequence(type_check,TS) :- _type_expressions(ES,TS).

_operator_variadic(OP) :- operator_declare_variadic(OP,T,RT,N).
_operator_variadicAccepts(OP,T) :- operator_declare_variadic(OP,T,RT,1).
_operator_variadicEmptyReturns(OP,RT) :- operator_declare_variadic(OP,T,RT,1).
_type_variadicListAux(OP,TS,N,NT,1) :- _expression(type_check,operation(OP,ARGS)), _type_expressions(ARGS,TS), _expression_sequenceLength(type_check,TS,N), _operator_variadicEmptyReturns(OP,NT).
_type_variadicListAux(OP,TS,IDX,IT,IR) :- _type_variadicListAux(OP,TS,IDX+1,NT,NR), _expression_sequenceIndex(type_check,TS,IDX,T), operator_declare_variadic(OP,T,IT,IR), IR > NR.
_type_variadicListAux(OP,TS,IDX,NT,NR) :- _type_variadicListAux(OP,TS,IDX+1,NT,NR), _expression_sequenceIndex(type_check,TS,IDX,T), operator_declare_variadic(OP,T,IT,IR), IR <= NR.
_type_expression(operation(OP,ARGS),T) :- _type_variadicListAux(OP,TS,0,T,R), _expression(type_check,operation(OP,ARGS)), _type_expressions(ARGS,TS).


%%%%%%%%%%%%%%%%% pythonExtract
_type_expression(operation(pythonExtract(STMT,EXPR),ARGS),bool) :- _expression(type_check,operation(pythonExtract(STMT,EXPR),ARGS)), EXPR  = "__succeeds".
_type_pythonExtractArgs(ARGS) :- _expression(type_check,operation(pythonExtract(STMT,EXPR),ARGS)).
_type_pythonExtractAux(ARGS,N,()) :- _type_pythonExtractArgs(ARGS), _expression_sequenceLength(type_check,ARGS,N).
_type_pythonExtractAux(ARGS,IDX,((X,T),L)) :- _type_pythonExtractAux(ARGS,IDX+1,L), _expression_sequenceIndex(type_check,ARGS,IDX,(val(string,X),EXPR)), _type_expression(EXPR,T).
_type_pythonExtract(STMT,EXPR,ARGS,TS,IDS) :- _expression(type_check,operation(pythonExtract(STMT,EXPR),ARGS)), _type_pythonExtractAux(ARGS,0,TS), _main_solverIdentifiers(IDS).
_type_pythonTypeExtractResult(operation(pythonExtract(STMT,EXPR),ARGS),T) :- _type_pythonExtract(STMT,EXPR,ARGS,TS,IDS), T=@pythonTypeExtract(STMT,EXPR,TS,IDS).
_type_expression(E,T) :- _type_pythonTypeExtractResult(E,valid(T)).
_warning(KIND,(),MSG) :- _type_pythonTypeExtractResult(E,error(KIND,MSG)).


%%%%%%%%%%%%%%%%% warnings

_type_expressionTyped(E) :- _type_expression(E,T), T!=bot.
_warning(type(noConsistentType),(),X) :- _passed(sugar,LBL,variable_interface(X)), _expression(type_check,variable(X)), not _type_expressionTyped(variable(X)).
_warning(type(untyped),(),X) :- _passed(sugar,LBL,variable_interface(X)), _type_expression(variable(X),top).


_warning(type(notSupported),(),operation(OP,ARGS)) :- _expression(type_check,operation(OP,ARGS)), not _type_expressionTyped(operation(OP,ARGS)).

type_expression(E,T) :- _type_expression(E,T), T != bot, not _type_expression(E,top).
type_expression(E,top) :- _type_expression(E,top).

%%%%%%%%%%%%%%%%% _expression_normal
_type_normalizeQuery(EXPR) :- _phase_active(type_check), _expression(sugar,LBL,DECL,EXPR).
_correction_expression(type_check,EXPR,bad) :-_type_normalizeQuery(EXPR), not _type_expressionTyped(EXPR).
