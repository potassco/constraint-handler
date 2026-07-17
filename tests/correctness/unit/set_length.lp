variable_define(empty,operation(set_make,())).
variable_define(values,operation(set_make,(val(int,1),(val(int,1),(val(none,none),()))))).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(length,(variable(empty),())).
evaluate(length,(variable(values),())).
evaluate(length,(variable(bad_case),())).

#show evaluated/3.
