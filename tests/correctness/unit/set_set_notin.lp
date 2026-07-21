variable_define(pool,operation(set_make,(val(int,1),(val(int,3),(val(none,none),()))))).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(int,1)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).


variable_define(bad_set,operation(set_make,(bad,()))).

evaluate(set_notin,(val(int,1),(variable(pool),()))).
evaluate(set_notin,(val(int,2),(variable(pool),()))).
evaluate(set_notin,(val(none,none),(variable(pool),()))).
evaluate(set_notin,(bad,(variable(pool),()))).
evaluate(set_notin,(val(int,1),(variable(bad_set),()))).
evaluate(set_notin,(variable(x),(variable(pool),()))).
evaluate(set_notin,(variable(x),(variable(bad_set),()))).
