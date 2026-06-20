% Flat union coverage for deterministic, nondeterministic, empty, and bad cases.

variable_define(a,operation(set_make,(val(int,1),(val(int,2),())))).
variable_define(b,operation(set_make,(val(int,2),(val(int,3),())))).
variable_define(empty,operation(set_make,())).

variable_define(ab,operation(union,(variable(a),(variable(b),())))).
variable_define(with_empty,operation(union,(variable(a),(variable(empty),(variable(b),()))))).
variable_define(empty_union,operation(union,(variable(empty),(variable(empty),())))).
variable_define(len_ab,operation(length,(variable(ab),()))).
variable_define(len_empty_union,operation(length,(variable(empty_union),()))).
evaluate(eq,(variable(with_empty),(variable(ab),()))).

set_declare(nd).
set_baseDomain(nd,val(int,4..5)).
set_assign(nd,val(int,4)).
variable_define(with_nd,operation(union,(variable(a),(variable(nd),())))).

variable_declare(bad_choice,fromFacts).
variable_domain(bad_choice,bad).
variable_define(bad_set,operation(set_make,(variable(bad_choice),()))).
variable_define(union_bad,operation(union,(variable(a),(variable(bad_set),())))).
