% Flat set membership coverage for deterministic, nondeterministic, empty, none, and bad cases.

variable_define(pool,operation(set_make,(val(string,"A"),(val(string,"B"),(val(none,none),()))))).
variable_define(empty,operation(set_make,())).

evaluate(operation(set_isin,(val(string,"A"),(variable(pool),())))).
evaluate(operation(set_notin,(val(string,"A"),(variable(pool),())))).
evaluate(operation(set_isin,(val(string,"Z"),(variable(pool),())))).
evaluate(operation(set_notin,(val(string,"Z"),(variable(pool),())))).
evaluate(operation(set_isin,(val(none,none),(variable(pool),())))).
evaluate(operation(set_notin,(val(none,none),(variable(empty),())))).

variable_declare(nd,set).
set_baseDomain(nd,val(int,1..2)).
set_assign(nd,val(int,1)).

evaluate(operation(set_isin,(val(int,1),(variable(nd),())))).
evaluate(operation(set_notin,(val(int,1),(variable(nd),())))).
evaluate(operation(set_isin,(val(int,2),(variable(nd),())))).
evaluate(operation(set_notin,(val(int,2),(variable(nd),())))).

variable_declare(bad_elem,fromFacts).
variable_domain(bad_elem,bad).
variable_define(bad_set,operation(set_make,(variable(bad_elem),()))).

evaluate(operation(set_isin,(variable(bad_elem),(variable(pool),())))).
evaluate(operation(set_notin,(variable(bad_elem),(variable(pool),())))).
evaluate(operation(set_isin,(val(int,1),(variable(bad_set),())))).
evaluate(operation(set_notin,(val(int,1),(variable(bad_set),())))).
