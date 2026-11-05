variable_define(ok,val(bool,false)).

variable_declare(a,set,val(bool,true),d_a1).
variable_declare(a,boolDomain,val(bool,true),d_a2).

warning_forbid(variable(multipleDeclarations),d_a1).
