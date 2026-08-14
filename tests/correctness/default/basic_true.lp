variable_declare(x,open).
variable_declare(y,open).
variable_declare(z,open).
variable_declare(t,open).
variable_declare(u,open).

variable_assign(x,val(int,4)).

variable_default(y,variable(x),val(bool,true)).
variable_default(z,variable(x)).
variable_default(t,variable(x),val(bool,true),13).
variable_default(some_label,u,variable(x),val(bool,true),2).
