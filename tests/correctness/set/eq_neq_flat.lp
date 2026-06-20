% Flat eq/neq coverage for deterministic, nondeterministic, empty, mixed-type, and bad cases.

variable_define(s1,operation(set_make,(val(int,1),(val(int,2),(val(int,2),()))))).
variable_define(s2,operation(set_make,(val(int,2),(val(int,1),())))).
variable_define(empty,operation(set_make,())).

evaluate(eq,(variable(s1),(variable(s2),()))).
evaluate(neq,(variable(s1),(variable(s2),()))).
evaluate(eq,(variable(empty),(operation(set_make,()),()))).
evaluate(neq,(variable(empty),(operation(set_make,()),()))).
evaluate(eq,(variable(s1),(val(int,1),()))).
evaluate(neq,(val(int,1),(variable(s1),()))).

set_declare(nd).
set_baseDomain(nd,val(int,1..2)).
set_assign(nd,val(int,1)).
variable_define(fixed,operation(set_make,(val(int,1),()))).
evaluate(eq,(variable(nd),(variable(fixed),()))).
evaluate(neq,(variable(nd),(variable(fixed),()))).

variable_declare(bad_choice,fromFacts).
variable_domain(bad_choice,bad).
evaluate(eq,(variable(bad_choice),(variable(s1),()))).
evaluate(neq,(variable(bad_choice),(variable(s1),()))).
variable_define(bad_set,operation(set_make,(variable(bad_choice),()))).
evaluate(eq,(variable(s1),(variable(bad_set),()))).
evaluate(neq,(variable(s1),(variable(bad_set),()))).
