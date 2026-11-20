variable_declare(inner,set).
set_assign(inner,val(int,2)).
set_assign(inner,val(int,3)).

variable_declare(nested,set).
set_assign(nested,variable(inner)).

variable_declare(pairs,set).
set_assign(pairs,(val(int,2),val(int,3))).

variable_define(nested_sum,operation(pythonExtract("","sum(sum(member) for member in pool)"),((val(string,"pool"),variable(nested)),()))).
variable_define(tuple_sum,operation(pythonExtract("","sum(sum(member) for member in pool)"),((val(string,"pool"),variable(pairs)),()))).