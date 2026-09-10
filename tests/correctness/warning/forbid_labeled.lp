variable_define(ok,val(bool,false)).

variable_define(b,val(bool,true),d_b1).
variable_define(b,operation(lnot,(val(bool,false),())),d_b2).

warning_forbid(variable(multipleDefinitions),ok).
warning_forbid(variable(multipleDefinitions),d_a1).
