#defined type_query/1.

%%%%%%%%%%%%%%%%% type_variable

type_variable((),X,T) :- variable_define(_,X,D), type_expression((),D,T).
type_variable((),X,none) :- variable_declareOptional(X).
type_variable((),X,bool) :- variable_declare(_,X,boolDomain).
type_variable((),X,T) :- variable_declare(_,X,fromFacts), variable_domain(X,D), type_expression((),D,T).
type_variable((),X,T) :- variable_declare(_,X,fromList(L)), D=@pythonListElements(L), type_expression((),D,T).
type_variable((), X, set) :- set_declare(_, X).
type_variable((), X, multimap) :- multimap_declare(_, X).
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

_warning(type(failed_operation),(),(SCOPE,O,ARGS)) :- _expression_query(SCOPE,E), E=operation(O,ARGS), not type_expression(SCOPE,E,_).


%%%%%%%%%%%%%%%%% type_operator
% Types
_type(int;float;bool;str;symbol;none;set;multimap).
_numeric_type(int;float).

% Operators
numericUnFOperator(sqrt;cos;sin;tan;acos;asin;atan).
numericUnOperator(abs;minus).
numericBinOperator(add;sub;mult;div;fdiv;pow;max).
comparisonOperator(leq;lt;geq;gt).
equalityOperator(eq;neq).
logicOperator(conj;disj;limp;lxor;leqv).
setOperator(union;inter;diff;subset).
membershipOperator(isin;notin).

% All
operator_declare(OP,(T1,(T2,())),bool) :- equalityOperator(OP), _type(T1),_type(T2), 1 { T1 = T2 ; T1 = none ; T2 = none }.
operator_declare(OP,(T,(T,())),bool) :- comparisonOperator(OP), _type(T), T != str.
% Numeric
operator_declare(OP,(T1,(T2,())),bool) :- comparisonOperator(OP), _numeric_type(T1), _numeric_type(T2).
operator_declare(OP,(T,()),float) :- numericUnFOperator(OP), _numeric_type(T).
operator_declare(OP,(T,()),T) :- numericUnOperator(OP), _numeric_type(T).
operator_declare(OP,(T,(T,())),float) :- _numeric_type(T), OP = fdiv.
operator_declare(OP,(T,(T,())),int) :- _numeric_type(T), OP = floor.
operator_declare(OP,(T,(T,())),T)    :- numericBinOperator(OP), _numeric_type(T), OP != fdiv.
operator_declare(OP,(T1,(T2,())),float) :- numericBinOperator(OP), _numeric_type(T1), _numeric_type(T2), T1 != T2.
% Bool
operator_declare(OP,(T,()),T) :- OP = lnot,T = (bool;none).
operator_declare(OP,(T,()),bool) :- OP = (wnot;snot), T = (bool;none).
operator_declare(OP,(T,(T,())),T) :- logicOperator(OP), T = (bool).
% Str
operator_declare(concat,(str,(str,())),str).
operator_declare(length,(T,()),int) :- T = (str;set).

% Set
operator_declare(OP,(T,(T,())),T) :- setOperator(OP), T = (set), OP != subset.
operator_declare(OP,(T,(T,())),bool) :- T = (set), OP = subset.
operator_declare(OP,(T,(set,())),bool) :- _type(T), membershipOperator(OP).

% Multimap
operator_declare(OP,(T,()),int) :- T = (multimap), OP = (countKeys;countEntries;sumIntEntries).
operator_declare(OP,(T1,()),T2) :- T1 = (multimap),_type(T2), T2 != (multimap), OP = (maxEntries;minEntries).
operator_declare(OP,(T1,(T2,())),bool) :- _type(T1), T2 = (multimap), membershipOperator(OP), OP != notin.

% Conditionals
operator_declare(OP,(T,()),bool) :- _type(T), OP = hasValue.

_type_operator((),O,function(TS,T)) :- operator_declare(O,TS,T).

% Variadic operators
%
variadicOperator(add;mult).
variadicOperator(OP) :- logicOperator(OP), OP != limp.

_variadic_check(SCOPE, OP, ARGS,0,T) :-
    _expression_query(SCOPE,E),
    E=operation(OP,ARGS),
    _type_listArg(SCOPE, ARGS, 0, ARG),
    type_expression(SCOPE,ARG,T),
    variadicOperator(OP).

_variadic_check(SCOPE, OP, ARGS,I,T) :-
    _expression_query(SCOPE,E),
    E=operation(OP,ARGS),
    _variadic_check(SCOPE,OP,ARGS,I-1,T1),
    _type_listArg(SCOPE, ARGS, I, ARG),
    type_expression(SCOPE,ARG,T2),
    operator_declare(OP, (T1, (T2,())), T).

_type_operator(SCOPE,OP,function((),T)) :-
    _expression_query(SCOPE,E),
    E=operation(OP,()),
    operator_declare(OP, (_, (_,())), T),
    variadicOperator(OP).

_type_operator(SCOPE,OP,function(TS,T)) :-
    _expression_query(SCOPE,E),
    E=operation(OP,ARGS),
    _type_listAux(SCOPE,ARGS,N,()),
    _variadic_check(SCOPE, OP, ARGS,N-1,T),
    _type_list(SCOPE,ARGS,TS).

% More complex operators (union types needed?)
operator_declare(ite,(bool,(int,(int,()))),int).
