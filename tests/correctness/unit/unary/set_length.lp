variable_define(empty,operation(set_make,())).
variable_define(values,operation(set_make,(val(int,1),(val(int,1),(val(none,none),()))))).


variable_declare(x,fromFacts).
variable_domain(x,variable(empty)).
variable_domain(x,variable(values)).
variable_domain(x,bad).
evaluate(length,(variable(x),())).

evaluate(length,(variable(empty),())).
evaluate(length,(variable(values),())).
evaluate(length,(bad,())).
