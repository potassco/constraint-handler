variable_declare(x,boolDomain).
variable_declare(y,boolDomain).
variable_declareOptional(y).
variable_declare(z,boolDomain).

ensure(operation(conj,(variable(x),(operation(lnot,(variable(y),())),())))).
