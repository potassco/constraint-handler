% Regression: zero-argument lambda application
% Should work across engines; assert via value/2.

define(dummy,f,(),val(int,5)).

variable_define(dummy,r,operation(variable(f),())).
