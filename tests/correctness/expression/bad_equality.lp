variable_declare(x,fromFacts).
variable_domain(x,val(bool,true)).
variable_domain(x,val(int,1)).
variable_domain(x,val(string,"hello")).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(eq,(variable(x),(bad,())))).

variable_define(y,variable(x)).
evaluate(operation(eq,(bad,(variable(y),())))).
