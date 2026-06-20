% Flat subset coverage for deterministic, nondeterministic, empty, and bad cases.

variable_define(a,operation(set_make,(val(int,1),(val(int,2),())))).
variable_define(b,operation(set_make,(val(int,1),(val(int,2),(val(int,3),()))))).
variable_define(empty,operation(set_make,())).

evaluate(subset,(variable(a),(variable(b),()))).
evaluate(subset,(variable(b),(variable(a),()))).
evaluate(subset,(variable(empty),(variable(a),()))).
evaluate(subset,(variable(a),(variable(empty),()))).

set_declare(nd).
set_baseDomain(nd,val(int,1..3)).
set_assign(nd,val(int,(1;2))).

evaluate(subset,(variable(a),(variable(nd),()))).
evaluate(subset,(variable(b),(variable(nd),()))).

variable_declare(bad_choice,fromFacts).
variable_domain(bad_choice,bad).
variable_define(bad_set,operation(set_make,(variable(bad_choice),()))).
evaluate(subset,(variable(a),(variable(bad_set),()))).
