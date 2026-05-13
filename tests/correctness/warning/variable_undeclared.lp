%%% raises warning(variable(undeclared),(),a) etc.
multimap_assign(a,val(string,"hello"),val(int,0)).
set_assign(b,val(string,"good bye")).
variable_domain(c,val(symbol,(red;green;blue))).
variable_domain(d,val(int,0..5)).

variable_define(e,variable(c)).
variable_define(f,variable(g)).
