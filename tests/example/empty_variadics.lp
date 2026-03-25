% Regression: empty variadic operators
% These should work across engines; assert via value/2.

variable_define(d,add0,operation(add,())).
variable_define(d,mult0,operation(mult,())).
variable_define(d,conj0,operation(conj,())).
variable_define(d,disj0,operation(disj,())).
variable_define(d,lxor0,operation(lxor,())).
variable_define(d,leqv0,operation(leqv,())).
