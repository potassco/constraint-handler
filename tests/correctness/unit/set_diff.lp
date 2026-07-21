variable_define(a,operation(set_make,(val(int,1),(val(int,2),(val(none,none),()))))).
variable_define(b,operation(set_make,(val(int,2),()))).
variable_define(empty,operation(set_make,())).


variable_declare(x,fromFacts).
variable_domain(x,operation(set_make,(val(int,1),(val(int,2),(val(none,none),()))))).
variable_domain(x,operation(set_make,())).
variable_domain(x,bad).


variable_define(bad_set,operation(set_make,(bad,()))).

evaluate(eq,(operation(diff,(variable(a),(variable(b),()))),(operation(set_make,(val(int,1),(val(none,none),()))),()))).
evaluate(eq,(operation(diff,(variable(a),(variable(empty),()))),(variable(a),()))).
evaluate(length,(operation(diff,(variable(empty),(variable(a),()))),())).
evaluate(length,(operation(diff,(variable(a),(variable(bad_set),()))),())).
evaluate(length,(operation(diff,(variable(x),(variable(b),()))),())).
evaluate(length,(operation(diff,(variable(x),(variable(bad_set),()))),())).
