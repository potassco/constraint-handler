variable_define(f,val(float,float("1.5"))).
variable_define(n,val(none,none)).
variable_define(s,val(string,"x")).

evaluate(eq,(variable(f),(variable(n),()))).
evaluate(eq,(variable(n),(variable(f),()))).
evaluate(neq,(variable(n),(variable(f),()))).

evaluate(eq,(variable(f),(variable(s),()))).
evaluate(eq,(variable(s),(variable(f),()))).
evaluate(neq,(variable(f),(variable(s),()))).
evaluate(neq,(variable(s),(variable(f),()))).
