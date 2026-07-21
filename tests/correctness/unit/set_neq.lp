variable_define(left,operation(set_make,(val(int,1),(val(none,none),())))).
variable_define(same,operation(set_make,(val(none,none),(val(int,1),(val(int,1),()))))).
variable_define(right,operation(set_make,(val(int,1),(val(int,2),(val(none,none),()))))).
variable_define(empty,operation(set_make,())).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,operation(set_make,(val(int,1),(val(none,none),())))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).


variable_define(bad_set,operation(set_make,(bad,()))).

evaluate(neq,(variable(left),(variable(same),()))).
evaluate(neq,(variable(left),(variable(right),()))).
evaluate(neq,(variable(empty),(operation(set_make,()),()))).
evaluate(neq,(variable(left),(val(none,none),()))).
evaluate(neq,(bad,(variable(left),()))).
evaluate(neq,(variable(left),(variable(bad_set),()))).
evaluate(neq,(variable(x),(variable(right),()))).
evaluate(neq,(variable(x),(val(none,none),()))).
evaluate(neq,(variable(x),(bad,()))).
