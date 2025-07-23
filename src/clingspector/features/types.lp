% Collect information about types.

% A variable has the type of its defining expression
cs__variable_type(V,T) :- assign(_, V, E), cs__expression_type(E,T).

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
cs_unsupported_argument_type(O, (ARG_T)) :- cs__expression(E),
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

% #show cs__expression/1.
% #show cs__expression_type/2.
% #show cs__variable_type/2.
#show cs_unsupported_operator_type/1.
#show eargs/4.
#show cs_unsupported_type/1.
#show cs_unsupported_argument_type/2.
