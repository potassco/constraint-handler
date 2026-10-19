variable_define(ok,val(bool,false)).

variable_declare(a,set,d_a1).
variable_declare(a,boolDomain,d_a2).

warning_forbid(variable(multipleDeclarations),d_a1).
