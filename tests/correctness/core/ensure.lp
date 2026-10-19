variable_declare(x,boolDomain).
variable_declare(y,definition).
variable_declare(enabled,boolDomain).

variable_define(y,val(bool,true),variable(enabled)).

ensure(variable(x)).
ensure(operation(eq,(variable(x),(val(bool,true),()))),labeled).
ensure(variable(y)).