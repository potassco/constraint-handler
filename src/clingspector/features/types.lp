% Collect information about types.

%
% Variables
%

% A variable has the type of its defining expression
cs__variable_type(V, T) :- assign(_, V, E), cs__expression_type(E,T).

% A variable is a set if there exists a set definition for it
cs__variable_type(V, set) :- cs__defined_set(V).

% A variable is a multimap if there exists a multimap definition for it
cs__variable_type(V, multimap) :- cs__defined_multimap(V).

% A key of a multimap has the type of the key's expression
cs__variable_type((MAP, key), T) :- cs__defined_multimap(MAP),
                                    multimap_assign(_, MAP, KEY, _),
                                    cs__expression_type(KEY, T).

% A value of a multimap has the type of the value's expression
cs__variable_type((MAP, val), T) :-   cs__defined_multimap(MAP),
                                    multimap_assign(_, MAP, _, VAL),
                                    cs__expression_type(VAL, T).

%
% Expressions
%

% An expression that is a value has the type of that value
cs__expression_type(E,T) :- cs__expression(E), E=val(T, _).

% An expression that is a variable has the type of that variable
cs__expression_type(E,T) :- cs__expression(E), E=variable(V), cs__variable_type(V,T).

% If an expression is a valid operation,
% it has the type of that operation's return type

% Unary
cs__expression_type(E,T) :- cs__expression(E),
                E=operation(O, ARGUMENTS),
                ARGUMENTS=(ARG, ()),
                cs__expression_type(ARG, ARG_T),
                cs__valid_operation(O, (ARG_T, ()), T).
% Binary
cs__expression_type(E,T) :- cs__expression(E),
                E=operation(O, ARGUMENTS),
                ARGUMENTS=(ARG_1, (ARG_2, ())),
                cs__expression_type(ARG_1, ARG_1_T),
                cs__expression_type(ARG_2, ARG_2_T),
                cs__valid_operation(O, (ARG_1_T, (ARG_2_T, ())), T).

%
% Unsupported types
%

% A type is unsupported if it is not in cs__type
cs_unsupported_type(T) :- cs__expression(E), E=val(T,_), not cs__type(T).
% An operator is unsupported if it is not in cs__operator
cs_unsupported_operator_type(O) :- cs__expression(E), E=operation(O,_), not cs__operator(O).

% An operation is unsupported if its operator is valid
% but there exists no valid operation with the given types

% Unary
cs_unsupported_argument_type(O, (ARG_T,)) :- cs__expression(E),
                E=operation(O, ARGUMENTS),
                ARGUMENTS=(ARG, ()),
                cs__expression_type(ARG, ARG_T),
                cs__operator(O),
                not cs__valid_operation(O, (ARG_T, ()), _).
% Binary
cs_unsupported_argument_type(O, (ARG_1_T, ARG_2_T)) :- cs__expression(E),
                E=operation(O, ARGUMENTS),
                ARGUMENTS=(ARG_1, (ARG_2, ())),
                cs__expression_type(ARG_1, ARG_1_T),
                cs__expression_type(ARG_2, ARG_2_T),
                cs__operator(O),
                not cs__valid_operation(O, (ARG_1_T, (ARG_2_T, ())), _).
%
% Type Mismatches
%
cs_type_mismatch(X, T_1, T_2) :- cs__variable_type(X, T_1), cs__variable_type(X, T_2), T_1 < T_2.
cs_type_mismatch(X, set, T) :- set_assign(_,X,_), cs__defined(X), not cs__defined_set(X), cs__variable_type(X, T).
cs_type_mismatch(X, multimap, T) :- multimap_assign(_,X,_,_), cs__defined(X), not cs__defined_multimap(X), cs__variable_type(X, T).

#show cs_unsupported_operator_type/1.
#show cs_unsupported_type/1.
#show cs_unsupported_argument_type/2.
#show cs_type_mismatch/3.
