variable_define(small,operation(set_make,(val(int,1),(val(none,none),())))).
variable_define(big,operation(set_make,(val(int,1),(val(int,2),(val(none,none),()))))).
variable_define(empty,operation(set_make,())).

variable_declare(bad_arg,fromFacts).
variable_domain(bad_arg,bad).
variable_define(bad_set,operation(set_make,(variable(bad_arg),()))).

evaluate(subset,(variable(small),(variable(big),()))).
evaluate(subset,(variable(big),(variable(small),()))).
evaluate(subset,(variable(empty),(variable(big),()))).
evaluate(subset,(variable(small),(variable(bad_set),()))).

#show evaluated/3.
