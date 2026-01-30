%%% raises warning(variable(undeclared),(),a) etc.
multimap_assign(d_a,a,val(str,"hello"),val(int,0)).
set_assign(d_b,b,val(str,"good bye")).
variable_domain(c,val(symbol,(red;green;blue))).
variable_domain(d,val(int,0..5)).

variable_define(d_e,e,variable(c)).
variable_define(d_f,f,variable(g)).
