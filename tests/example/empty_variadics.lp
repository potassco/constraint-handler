% Regression: empty variadic operators
% These should work across engines; assert via value/2.

variable_define(add0,operation(add,())).
variable_define(mult0,operation(mult,())).
variable_define(conj0,operation(conj,())).
variable_define(disj0,operation(disj,())).
variable_define(lxor0,operation(lxor,())).
variable_define(leqv0,operation(leqv,())).
