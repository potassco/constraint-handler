variable_define(ok,val(bool,false)).

variable_declare(a,set,val(bool,true),d_a1).
variable_declare(a,boolDomain,val(bool,true),d_a2).
variable_declare(b,set,val(bool,true),d_b1).
variable_declare(b,boolDomain,val(bool,true),d_b2).

warning_ignore(variable(multipleDeclarations),d_a1).
