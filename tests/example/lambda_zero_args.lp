% Regression: zero-argument lambda application
% Should work across engines; assert via value/2.

define(f,(),val(int,5)).

variable_define(r,operation(variable(f),())).
