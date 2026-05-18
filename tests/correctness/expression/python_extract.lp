variable_define(x,val(int,3)).
variable_define(y,val(int,4)).

variable_define(z,operation(pythonExtract("tmp = lhs * rhs","tmp + rhs"),((val(string,"lhs"),variable(x)),((val(string,"rhs"),variable(y)),())))).
variable_define(t,operation(pythonExtract("lhs = lhs + 2","lhs == 5"),((val(string,"lhs"),variable(x)),()))).
variable_define(u,operation(pythonExtract("lhs = lhs + 3","lhs == 7"),((val(string,"lhs"),variable(x)),()))).

#show value/2.
#show warning/3.
