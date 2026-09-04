%%% float compared with none/string for eq/neq
variable_define(f,val(float,float("1.5"))).
variable_define(n,val(none,none)).
variable_define(s,val(string,"x")).

evaluate(operation(eq,(variable(f),(variable(n),())))).
evaluate(operation(eq,(variable(n),(variable(f),())))).
evaluate(operation(neq,(variable(n),(variable(f),())))).

evaluate(operation(eq,(variable(f),(variable(s),())))).
evaluate(operation(eq,(variable(s),(variable(f),())))).
evaluate(operation(neq,(variable(f),(variable(s),())))).
evaluate(operation(neq,(variable(s),(variable(f),())))).
