variable_define(left,operation(set_make,(val(int,1),(val(none,none),())))).
variable_define(same,operation(set_make,(val(none,none),(val(int,1),(val(int,1),()))))).
variable_define(right,operation(set_make,(val(int,1),(val(int,2),(val(none,none),()))))).
variable_define(empty,operation(set_make,())).

variable_declare(none_scalar,fromFacts).
variable_domain(none_scalar,val(none,none)).

variable_declare(bad_arg,fromFacts).
variable_domain(bad_arg,bad).
variable_define(bad_set,operation(set_make,(variable(bad_arg),()))).

evaluate(neq,(variable(left),(variable(same),()))).
evaluate(neq,(variable(left),(variable(right),()))).
evaluate(neq,(variable(empty),(operation(set_make,()),()))).
evaluate(neq,(variable(left),(variable(none_scalar),()))).
evaluate(neq,(variable(bad_arg),(variable(left),()))).
evaluate(neq,(variable(left),(variable(bad_set),()))).

#show evaluated/3.
