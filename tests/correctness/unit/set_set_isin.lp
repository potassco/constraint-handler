variable_define(pool,operation(set_make,(val(int,1),(val(int,3),(val(none,none),()))))).

variable_declare(bad_elem,fromFacts).
variable_domain(bad_elem,bad).

variable_define(bad_set,operation(set_make,(variable(bad_elem),()))).

evaluate(set_isin,(val(int,1),(variable(pool),()))).
evaluate(set_isin,(val(int,2),(variable(pool),()))).
evaluate(set_isin,(val(none,none),(variable(pool),()))).
evaluate(set_isin,(variable(bad_elem),(variable(pool),()))).
evaluate(set_isin,(val(int,1),(variable(bad_set),()))).

#show evaluated/3.
