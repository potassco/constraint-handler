variable_define(ok,val(bool,false)).

variable_declare(a,set,d_a1).
variable_declare(a,boolDomain,d_a2).
variable_declare(b,set,d_b1).
variable_declare(b,boolDomain,d_b2).

warning_ignore(variable(multipleDeclarations),d_a1).
