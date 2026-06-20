% Simple nondeterministic declared set regression.

set_declare(s).
set_baseDomain(s,val(int,1..2)).
set_assign(s,val(int,1)).

evaluate(set_isin,(val(int,1),(variable(s),()))).
evaluate(set_notin,(val(int,1),(variable(s),()))).
evaluate(set_isin,(val(int,2),(variable(s),()))).
evaluate(set_notin,(val(int,2),(variable(s),()))).
