variable_define(ok,val(bool,false)).

variable_define(d_a1,a,val(bool,true)).
variable_define(d_a2,a,operation(lnot,(val(bool,true),()))).

warning_forbid(variable(multipleDefinitions),d_a1).
