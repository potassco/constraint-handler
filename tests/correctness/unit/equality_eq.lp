evaluate(operation(eq,(val(bool,true),(val(bool,true),())))).
evaluate(operation(eq,(val(bool,true),(val(bool,false),())))).
evaluate(operation(eq,(val(int,1),(val(int,1),())))).
evaluate(operation(eq,(val(int,1),(val(int,2),())))).
evaluate(operation(eq,(val(none,none),(val(none,none),())))).
evaluate(operation(eq,(val(string,"foo"),(val(string,"foo"),())))).
evaluate(operation(eq,(val(string,"foo"),(val(string,"bar"),())))).
evaluate(operation(eq,(val(symbol,red),(val(symbol,red),())))).
evaluate(operation(eq,(val(symbol,red),(val(symbol,blue),())))).
evaluate(operation(eq,(val(bool,true),(val(none,none),())))).
evaluate(operation(eq,(val(none,none),(val(bool,true),())))).
evaluate(operation(eq,(val(bool,true),(bad,())))).
evaluate(operation(eq,(bad,(val(bool,true),())))).


variable_declare(x,fromFacts).
variable_domain(x,val(int,1)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(eq,(variable(x),(val(int,1),())))).
evaluate(operation(eq,(variable(x),(val(none,none),())))).
evaluate(operation(eq,(variable(x),(bad,())))).
