variable_define(tuple_plain,(val(int,1),val(string,"x"),val(symbol,key))).
variable_define(tuple_plain_same,variable(tuple_plain)).
variable_define(tuple_diff,(val(int,2),val(string,"x"),val(symbol,key))).

variable_define(tuple_with_none,(val(none,none),val(int,1))).
variable_define(tuple_with_none_same,variable(tuple_with_none)).

evaluate(operation(neq,(variable(tuple_plain),(variable(tuple_plain_same),())))).
evaluate(operation(neq,(variable(tuple_plain),(variable(tuple_diff),())))).
evaluate(operation(neq,(variable(tuple_with_none),(variable(tuple_with_none_same),())))).
evaluate(operation(neq,(variable(tuple_plain),(variable(tuple_with_none),())))).
evaluate(operation(neq,(variable(tuple_plain),(val(none,none),())))).
evaluate(operation(neq,(val(none,none),(variable(tuple_plain),())))).
evaluate(operation(neq,(variable(tuple_plain),(bad,())))).
evaluate(operation(neq,(bad,(variable(tuple_plain),())))).


variable_declare(x,fromFacts).
variable_domain(x,(val(int,1),val(string,"x"),val(symbol,key))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(neq,(variable(x),((val(int,1),val(string,"x"),val(symbol,key)),())))).
evaluate(operation(neq,(variable(x),(val(none,none),())))).
evaluate(operation(neq,(variable(x),(bad,())))).
