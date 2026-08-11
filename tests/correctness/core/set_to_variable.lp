% Make sure a set can be assigned directly to a new variable.
variable_declare(x,set).
set_assign(x,val(string,"a")).
variable_declare(y,definition).
variable_define(y,variable(x)).
