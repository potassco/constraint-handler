variable_define(tuple_plain,(val(int,1),val(string,"x"),val(symbol,key))).
variable_define(tuple_plain_same,variable(tuple_plain)).
variable_define(tuple_diff,(val(int,2),val(string,"x"),val(symbol,key))).

variable_define(tuple_with_none,(val(none,none),val(int,1))).
variable_define(tuple_with_none_same,variable(tuple_with_none)).

evaluate(eq,(variable(tuple_plain),(variable(tuple_plain_same),()))).
evaluate(eq,(variable(tuple_plain),(variable(tuple_diff),()))).
evaluate(eq,(variable(tuple_with_none),(variable(tuple_with_none_same),()))).
evaluate(eq,(variable(tuple_plain),(variable(tuple_with_none),()))).
evaluate(eq,(variable(tuple_plain),(val(none,none),()))).
evaluate(eq,(val(none,none),(variable(tuple_plain),()))).
evaluate(eq,(variable(tuple_plain),(bad,()))).
evaluate(eq,(bad,(variable(tuple_plain),()))).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,(val(int,1),val(string,"x"),val(symbol,key))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(eq,(variable(x),((val(int,1),val(string,"x"),val(symbol,key)),()))).
evaluate(eq,(variable(x),(val(none,none),()))).
evaluate(eq,(variable(x),(bad,()))).

