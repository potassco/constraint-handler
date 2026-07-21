variable_define(tuple_left,(val(int,1),val(string,"x"),val(symbol,key))).
variable_define(tuple_same,variable(tuple_left)).
variable_define(tuple_other,(val(int,2),val(string,"x"),val(symbol,key))).

evaluate(eq,(val(bool,true),(val(bool,true),()))).
evaluate(eq,(val(bool,true),(val(bool,false),()))).
evaluate(eq,(val(int,1),(val(int,1),()))).
evaluate(eq,(val(int,1),(val(int,2),()))).
evaluate(eq,(val(none,none),(val(none,none),()))).
evaluate(eq,(val(string,"foo"),(val(string,"foo"),()))).
evaluate(eq,(val(string,"foo"),(val(string,"bar"),()))).
evaluate(eq,(val(symbol,red),(val(symbol,red),()))).
evaluate(eq,(val(symbol,red),(val(symbol,blue),()))).
evaluate(eq,(variable(tuple_left),(variable(tuple_same),()))).
evaluate(eq,(variable(tuple_left),(variable(tuple_other),()))).
evaluate(eq,(val(bool,true),(val(none,none),()))).
evaluate(eq,(val(none,none),(val(bool,true),()))).
evaluate(eq,(val(bool,true),(bad,()))).
evaluate(eq,(bad,(val(bool,true),()))).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(int,1)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(eq,(variable(x),(val(int,1),()))).
evaluate(eq,(variable(x),(val(none,none),()))).
evaluate(eq,(variable(x),(bad,()))).

