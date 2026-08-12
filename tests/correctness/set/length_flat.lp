% Flat cardinality coverage for empty, duplicate, zero, nondeterministic, and bad inputs.

variable_define(empty,operation(set_make,())).
variable_define(with_zero,operation(set_make,(val(int,0),(val(int,0),(val(none,none),(val(none,none),())))))).
variable_define(len_empty,operation(cardinality,(variable(empty),()))).
variable_define(len_with_zero,operation(cardinality,(variable(with_zero),()))).

variable_declare(single_zero,set).
set_baseDomain(single_zero,val(int,0)).
set_assign(single_zero,val(int,0)).

variable_declare(nondeterministic,set).
set_baseDomain(nondeterministic,val(int,0..1)).

evaluate(cardinality,(variable(single_zero),())).
evaluate(cardinality,(variable(nondeterministic),())).
variable_define(from_declared,operation(set_make,(operation(cardinality,(variable(single_zero),())),(val(int,0),())))).
variable_define(len_from_declared,operation(cardinality,(variable(from_declared),()))).

variable_declare(bad_choice,fromFacts).
variable_domain(bad_choice,bad).
variable_define(bad_set,operation(set_make,(variable(bad_choice),()))).
variable_define(len_bad_set,operation(cardinality,(variable(bad_set),()))).

evaluate(cardinality,(variable(bad_choice),())).
