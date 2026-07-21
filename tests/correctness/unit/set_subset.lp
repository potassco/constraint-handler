variable_define(small,operation(set_make,(val(int,1),(val(none,none),())))).
variable_define(big,operation(set_make,(val(int,1),(val(int,2),(val(none,none),()))))).
variable_define(empty,operation(set_make,())).


variable_declare(x,fromFacts).
variable_domain(x,operation(set_make,(val(int,1),(val(none,none),())))).
variable_domain(x,operation(set_make,())).
variable_domain(x,bad).


variable_define(bad_set,operation(set_make,(bad,()))).

evaluate(subset,(variable(small),(variable(big),()))).
evaluate(subset,(variable(big),(variable(small),()))).
evaluate(subset,(variable(empty),(variable(big),()))).
evaluate(subset,(variable(small),(variable(bad_set),()))).
evaluate(subset,(variable(x),(variable(big),()))).
evaluate(subset,(variable(x),(variable(bad_set),()))).
