% Flat diff coverage for deterministic, nondeterministic, empty, and bad cases.

variable_define(a,operation(set_make,(val(int,1),(val(int,2),(val(int,3),()))))).
variable_define(b,operation(set_make,(val(int,2),()))).
variable_define(empty,operation(set_make,())).

variable_define(ab,operation(diff,(variable(a),(variable(b),())))).
variable_define(a_empty,operation(diff,(variable(a),(variable(empty),())))).
variable_define(empty_a,operation(diff,(variable(empty),(variable(a),())))).
variable_define(len_ab,operation(length,(variable(ab),()))).
variable_define(len_empty_a,operation(length,(variable(empty_a),()))).

set_declare(nd).
set_baseDomain(nd,val(int,2..3)).
set_assign(nd,val(int,2)).
variable_define(with_nd,operation(diff,(variable(a),(variable(nd),())))).

variable_declare(bad_choice,fromFacts).
variable_domain(bad_choice,bad).
variable_define(bad_set,operation(set_make,(variable(bad_choice),()))).
variable_define(diff_bad,operation(diff,(variable(a),(variable(bad_set),())))).
