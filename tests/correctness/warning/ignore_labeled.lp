variable_define(ok,val(bool,false)).

variable_define(a,val(bool,true),d_a1).
variable_define(a,operation(lnot,(val(bool,false),())),d_a2).
variable_define(b,val(bool,true),d_b1).
variable_define(b,operation(lnot,(val(bool,false),())),d_b2).

warning_ignore(variable(multipleDefinitions),d_a1).
