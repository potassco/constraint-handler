evaluate(operation(neq,(val(bool,true),(val(bool,true),())))).
evaluate(operation(neq,(val(bool,true),(val(bool,false),())))).
evaluate(operation(neq,(val(int,1),(val(int,1),())))).
evaluate(operation(neq,(val(int,1),(val(int,2),())))).
evaluate(operation(neq,(val(none,none),(val(none,none),())))).
evaluate(operation(neq,(val(string,"foo"),(val(string,"foo"),())))).
evaluate(operation(neq,(val(string,"foo"),(val(string,"bar"),())))).
evaluate(operation(neq,(val(symbol,red),(val(symbol,red),())))).
evaluate(operation(neq,(val(symbol,red),(val(symbol,blue),())))).
evaluate(operation(neq,(val(bool,true),(val(none,none),())))).
evaluate(operation(neq,(val(none,none),(val(bool,true),())))).
evaluate(operation(neq,(val(bool,true),(bad,())))).
evaluate(operation(neq,(bad,(val(bool,true),())))).


variable_declare(x,fromFacts).
variable_domain(x,val(int,1)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(neq,(variable(x),(val(int,1),())))).
evaluate(operation(neq,(variable(x),(val(none,none),())))).
evaluate(operation(neq,(variable(x),(bad,())))).
