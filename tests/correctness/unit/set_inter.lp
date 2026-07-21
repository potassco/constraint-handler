variable_define(a,operation(set_make,(val(int,1),(val(int,2),(val(none,none),()))))).
variable_define(b,operation(set_make,(val(int,2),(val(int,3),(val(none,none),()))))).
variable_define(empty,operation(set_make,())).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,operation(set_make,(val(int,1),(val(int,2),(val(none,none),()))))).
variable_domain(x,operation(set_make,())).
variable_domain(x,bad).


variable_define(bad_set,operation(set_make,(bad,()))).

evaluate(eq,(operation(inter,(variable(a),(variable(b),()))),(operation(set_make,(val(int,2),(val(none,none),()))),()))).
evaluate(length,(operation(inter,(variable(a),(variable(empty),()))),())).
evaluate(length,(operation(inter,(variable(a),(variable(bad_set),()))),())).
evaluate(length,(operation(inter,(variable(x),(variable(b),()))),())).
evaluate(length,(operation(inter,(variable(x),(variable(bad_set),()))),())).
