% Flat set_make coverage for deterministic, nondeterministic, empty, and bad cases.

variable_define(empty,operation(set_make,())).
variable_define(deterministic,operation(set_make,(val(int,1),(val(int,2),(val(int,1),(val(none,none),())))))).
variable_define(len_empty,operation(length,(variable(empty),()))).
variable_define(len_deterministic,operation(length,(variable(deterministic),()))).

evaluate(eq,(variable(deterministic),(operation(set_make,(val(none,none),(val(int,2),(val(int,1),())))),()))).

set_declare(source).
set_baseDomain(source,val(int,1..2)).
set_assign(source,val(int,1)).
variable_define(nondeterministic,operation(set_make,(operation(length,(variable(source),())),(val(int,9),())))).
variable_define(len_nondeterministic,operation(length,(variable(nondeterministic),()))).

variable_declare(bad_choice,fromFacts).
variable_domain(bad_choice,bad).
variable_define(made_bad,operation(set_make,(variable(bad_choice),(val(int,5),())))).
