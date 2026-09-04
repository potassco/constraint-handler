variable_define(left,operation(set_make,(val(int,1),(val(none,none),())))).
variable_define(same,operation(set_make,(val(none,none),(val(int,1),(val(int,1),()))))).
variable_define(right,operation(set_make,(val(int,1),(val(int,2),(val(none,none),()))))).
variable_define(empty,operation(set_make,())).


variable_declare(x,fromFacts).
variable_domain(x,operation(set_make,(val(int,1),(val(none,none),())))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).


variable_define(bad_set,operation(set_make,(bad,()))).

evaluate(operation(eq,(variable(left),(variable(same),())))).
evaluate(operation(eq,(variable(left),(variable(right),())))).
evaluate(operation(eq,(variable(empty),(operation(set_make,()),())))).
evaluate(operation(eq,(variable(left),(val(none,none),())))).
evaluate(operation(eq,(bad,(variable(left),())))).
evaluate(operation(eq,(variable(left),(variable(bad_set),())))).
evaluate(operation(eq,(variable(x),(variable(right),())))).
evaluate(operation(eq,(variable(x),(val(none,none),())))).
evaluate(operation(eq,(variable(x),(bad,())))).
