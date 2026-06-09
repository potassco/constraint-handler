variable_define(pool,operation(pythonExtract("vals = {lhs, rhs, lhs}","vals"),((val(string,"lhs"),val(int,1)),((val(string,"rhs"),val(int,3)),())))).
variable_define(size,operation(length,(variable(pool),()))).

#show value/2.
#show set_value/2.
