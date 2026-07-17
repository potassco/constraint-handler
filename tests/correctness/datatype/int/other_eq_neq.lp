variable_define(i,val(int,2)).
variable_define(n,val(none,none)).
variable_define(s,val(string,"x")).

evaluate(eq,(variable(i),(variable(n),()))).
evaluate(eq,(variable(n),(variable(i),()))).
evaluate(neq,(variable(i),(variable(n),()))).
evaluate(neq,(variable(n),(variable(i),()))).

evaluate(eq,(variable(i),(variable(s),()))).
evaluate(eq,(variable(s),(variable(i),()))).
evaluate(neq,(variable(i),(variable(s),()))).
evaluate(neq,(variable(s),(variable(i),()))).