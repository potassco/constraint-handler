variable_define(ok,val(bool,false)).

variable_define(d_a1,a,val(bool,true)).
variable_define(d_a2,a,operation(lnot,(val(bool,false),()))).
variable_define(d_b1,b,val(bool,true)).
variable_define(d_b2,b,operation(lnot,(val(bool,false),()))).

warning_ignore(variable(multipleDefinitions),d_a1).
