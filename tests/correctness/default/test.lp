default_mode(depends).

variable_domain(x,val(int,4)).
variable_default(x,val(int,1),val(bool,true)).

variable_define(y,val(int,4)).

variable_define(z,operation(eq,(variable(x),(variable(y),())))).

ensure(variable(z)).

#show _se_value/2.
