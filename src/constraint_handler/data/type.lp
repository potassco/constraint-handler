#defined type_query/1.

%%%%%%%%%%%%%%%%% type_variable

type_variable((),X,T) :- variable_define(_,X,D), type_expression((),D,T).
type_variable((),X,none) :- variable_declareOptional(X).
type_variable((),X,bool) :- variable_declare(_,X,boolDomain).
type_variable((),X,T) :- variable_declare(_,X,fromFacts), variable_domain(X,D), type_expression((),D,T).
type_variable((),X,T) :- variable_declare(_,X,fromList(L)), D=@pythonListElements(L), type_expression((),D,T).

%%%%%%%%%%%%%%%%% type_expression

_expression_query((),E) :- type_query(E).
type_expression(SCOPE,E,T) :- _expression_query(SCOPE,E), E=variable(X), type_variable(SCOPE,X,T).
type_expression(SCOPE,E,T) :- _expression_query(SCOPE,E), E=val(T,_).
type_expression(SCOPE,E,top) :- _expression_query(SCOPE,E), E=python(S).
type_expression(SCOPE,E,T) :- _expression_query(SCOPE,E), E=operation(O,ARGS), _type_operator(SCOPE,O,function(TS,T)), _type_list(SCOPE,ARGS,TS).

_type_listArg(SCOPE,ARGS,IDX,ARG) :- _expression_query(SCOPE,E), E=operation(O,ARGS), (IDX,ARG)=@pythonEnumerateElements(ARGS).
_type_listAux(SCOPE,ARGS,N,()) :- _expression_query(SCOPE,E), E=operation(O,ARGS), N=@pythonListLength(ARGS).
_type_listAux(SCOPE,ARGS,N-1,(T,TS)) :- _type_listAux(SCOPE,ARGS,N,TS), _type_listArg(SCOPE,ARGS,N-1,ARG), type_expression(SCOPE,ARG,T).
_type_list(SCOPE,ARGS,TS) :- _type_listAux(SCOPE,ARGS,0,TS).

% TODO lambdas


%%%%%%%%%%%%%%%%% type_statement
% TODO statements.

warning(type(failed_operation),(),(SCOPE,O,ARGS)) :- _expression_query(SCOPE,E), E=operation(O,ARGS), not type_expression(SCOPE,E,_).


%%% temporary stuff until more uniform handling of operators.
operator_declare(mult,(int,(int,())),int).
operator_declare(add,(int,(int,())),int).
operator_declare(ite,(bool,(int,(int,()))),int).

_type_operator((),O,function(TS,T)) :- operator_declare(O,TS,T).
