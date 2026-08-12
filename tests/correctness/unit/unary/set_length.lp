phase_request(constantFolding,false).

variable_define(empty,operation(set_make,())).
variable_define(values,operation(set_make,(val(int,1),(val(int,1),(val(none,none),()))))).


variable_declare(x,fromFacts).
variable_domain(x,variable(empty)).
variable_domain(x,variable(values)).
variable_domain(x,bad).
evaluate(cardinality,(variable(x),())).

evaluate(cardinality,(variable(empty),())).
evaluate(cardinality,(variable(values),())).
evaluate(cardinality,(bad,())).
