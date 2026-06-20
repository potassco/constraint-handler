variable_define(constant,python("2")).
variable_define(abs_value,operation(python("abs"),(val(int,-3),()))).
variable_define(sum_value,operation(python("lambda lhs, rhs: lhs + rhs"),(val(int,2),(val(int,5),())))).

#show value/2.
