variable_define(lhs,val(int,3)).
variable_define(rhs,val(int,4)).

variable_define(product_plus_rhs,operation(pythonExtract("tmp = lhs * rhs","tmp + rhs"),((val(string,"lhs"),variable(lhs)),((val(string,"rhs"),variable(rhs)),())))).
variable_define(lhs_is_five,operation(pythonExtract("lhs = lhs + 2","lhs == 5"),((val(string,"lhs"),variable(lhs)),()))).

#show value/2.
