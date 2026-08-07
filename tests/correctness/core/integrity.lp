variable_declare(x,boolDomain).
variable_declare(y,boolDomain).
variable_domain(y,val(none,none)).
variable_declare(z,boolDomain).

ensure(operation(conj,(variable(x),(operation(lnot,(variable(y),())),())))).
