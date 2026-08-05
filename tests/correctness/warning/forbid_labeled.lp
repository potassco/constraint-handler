variable_define(ok,val(bool,false)).

variable_define(d_b1,b,val(bool,true)).
variable_define(d_b2,b,operation(lnot,(val(bool,false),()))).

warning_forbid(variable(multipleDefinitions),ok).
warning_forbid(variable(multipleDefinitions),d_a1).
