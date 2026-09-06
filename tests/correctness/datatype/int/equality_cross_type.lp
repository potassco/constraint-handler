variable_define(i,val(int,2)).
variable_define(n,val(none,none)).
variable_define(s,val(string,"x")).

evaluate(operation(eq,(variable(i),(variable(n),())))).
evaluate(operation(eq,(variable(n),(variable(i),())))).
evaluate(operation(neq,(variable(i),(variable(n),())))).
evaluate(operation(neq,(variable(n),(variable(i),())))).

evaluate(operation(eq,(variable(i),(variable(s),())))).
evaluate(operation(eq,(variable(s),(variable(i),())))).
evaluate(operation(neq,(variable(i),(variable(s),())))).
evaluate(operation(neq,(variable(s),(variable(i),())))).
