variable_define(tuple_left,(val(int,1),val(string,"x"),val(symbol,key))).
variable_define(tuple_same,variable(tuple_left)).
variable_define(tuple_other,(val(int,2),val(string,"x"),val(symbol,key))).

evaluate(neq,(val(bool,true),(val(bool,true),()))).
evaluate(neq,(val(bool,true),(val(bool,false),()))).
evaluate(neq,(val(int,1),(val(int,1),()))).
evaluate(neq,(val(int,1),(val(int,2),()))).
evaluate(neq,(val(none,none),(val(none,none),()))).
evaluate(neq,(val(string,"foo"),(val(string,"foo"),()))).
evaluate(neq,(val(string,"foo"),(val(string,"bar"),()))).
evaluate(neq,(val(symbol,red),(val(symbol,red),()))).
evaluate(neq,(val(symbol,red),(val(symbol,blue),()))).
evaluate(neq,(variable(tuple_left),(variable(tuple_same),()))).
evaluate(neq,(variable(tuple_left),(variable(tuple_other),()))).
evaluate(neq,(val(bool,true),(val(none,none),()))).
evaluate(neq,(val(none,none),(val(bool,true),()))).
evaluate(neq,(val(bool,true),(bad,()))).
evaluate(neq,(bad,(val(bool,true),()))).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(int,1)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(neq,(variable(x),(val(int,1),()))).
evaluate(neq,(variable(x),(val(none,none),()))).
evaluate(neq,(variable(x),(bad,()))).

