% Flat inter coverage for deterministic, nondeterministic, empty, and bad cases.

variable_define(a,operation(set_make,(val(int,1),(val(int,2),(val(int,3),()))))).
variable_define(b,operation(set_make,(val(int,2),(val(int,3),(val(int,4),()))))).
variable_define(empty,operation(set_make,())).

variable_define(ab,operation(inter,(variable(a),(variable(b),())))).
variable_define(with_empty,operation(inter,(variable(a),(variable(empty),())))).
variable_define(len_ab,operation(length,(variable(ab),()))).
variable_define(len_with_empty,operation(length,(variable(with_empty),()))).

set_declare(nd).
set_baseDomain(nd,val(int,2..4)).
set_assign(nd,val(int,2)).
variable_define(with_nd,operation(inter,(variable(a),(variable(nd),())))).

variable_declare(bad_choice,fromFacts).
variable_domain(bad_choice,bad).
variable_define(bad_set,operation(set_make,(variable(bad_choice),()))).
variable_define(inter_bad,operation(inter,(variable(a),(variable(bad_set),())))).
