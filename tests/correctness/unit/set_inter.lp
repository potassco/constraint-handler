variable_define(a,operation(set_make,(val(int,1),(val(int,2),(val(none,none),()))))).
variable_define(b,operation(set_make,(val(int,2),(val(int,3),(val(none,none),()))))).
variable_define(empty,operation(set_make,())).

variable_declare(bad_arg,fromFacts).
variable_domain(bad_arg,bad).
variable_define(bad_set,operation(set_make,(variable(bad_arg),()))).

evaluate(eq,(operation(inter,(variable(a),(variable(b),()))),(operation(set_make,(val(int,2),(val(none,none),()))),()))).
evaluate(length,(operation(inter,(variable(a),(variable(empty),()))),())).
evaluate(length,(operation(inter,(variable(a),(variable(bad_set),()))),())).

#show evaluated/3.
