variable_declare(b,fromFacts).
variable_domain(b, val(int,3..4)).

variable_declare(a,fromFacts).
variable_domain(a,val(int,3)).
variable_domain(a,variable(b)).
