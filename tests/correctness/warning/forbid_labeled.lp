variable_define(ok,val(bool,false)).

variable_declare(b,set,d_b1).
variable_declare(b,set,d_b2).

warning_forbid(variable(multipleDeclarations),ok).
warning_forbid(variable(multipleDeclarations),d_a1).
