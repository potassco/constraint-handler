% Make sure a set can be assigned directly to a new variable.
set_declare(x).
set_assign(x,val(string,"a")).
variable_define(y, variable(x)).
