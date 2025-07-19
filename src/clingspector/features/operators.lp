% Collect all used operators.
%
% This is used to identify unsupported operators in expressions.

cs_operator(O) :- cs__expression(E), E=operation(O,_).

#show cs_operator/1.