variable_define(ok,val(bool,false)).

variable_define(a,val(bool,true),d_a1).
variable_define(a,operation(lnot,(val(bool,true),())),d_a2).

warning_forbid(variable(multipleDefinitions),d_a1).
