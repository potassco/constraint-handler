variable_define(empty,operation(set_make,())).
variable_define(values,operation(set_make,(val(int,1),(val(int,1),(val(none,none),()))))).


variable_declare(x,fromFacts).
variable_domain(x,variable(empty)).
variable_domain(x,variable(values)).
variable_domain(x,bad).
evaluate(operation(cardinality,(variable(x),()))).

evaluate(operation(cardinality,(variable(empty),()))).
evaluate(operation(cardinality,(variable(values),()))).
evaluate(operation(cardinality,(bad,()))).
