% Flat length coverage for empty, duplicate, zero, nondeterministic, and bad inputs.

variable_define(empty,operation(set_make,())).
variable_define(with_zero,operation(set_make,(val(int,0),(val(int,0),(val(none,none),(val(none,none),())))))).
variable_define(len_empty,operation(length,(variable(empty),()))).
variable_define(len_with_zero,operation(length,(variable(with_zero),()))).

set_declare(single_zero).
set_baseDomain(single_zero,val(int,0)).
set_assign(single_zero,val(int,0)).

set_declare(nondeterministic).
set_baseDomain(nondeterministic,val(int,0..1)).

evaluate(length,(variable(single_zero),())).
evaluate(length,(variable(nondeterministic),())).
variable_define(from_declared,operation(set_make,(operation(length,(variable(single_zero),())),(val(int,0),())))).
variable_define(len_from_declared,operation(length,(variable(from_declared),()))).

variable_declare(bad_choice,fromFacts).
variable_domain(bad_choice,bad).
variable_define(bad_set,operation(set_make,(variable(bad_choice),()))).
variable_define(len_bad_set,operation(length,(variable(bad_set),()))).

evaluate(length,(variable(bad_choice),())).
