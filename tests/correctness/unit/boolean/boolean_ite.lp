evaluate(ite,(val(bool,true),(val(int,1),(val(string,"else"),())))).
evaluate(ite,(val(bool,false),(val(int,1),(val(string,"else"),())))).
evaluate(ite,(val(none,none),(val(int,1),(val(string,"else"),())))).
evaluate(ite,(bad,(val(int,1),(val(string,"else"),())))).
evaluate(ite,(val(bool,true),(bad,(val(string,"else"),())))).
evaluate(ite,(val(bool,false),(bad,(val(string,"else"),())))).
evaluate(ite,(val(bool,false),(val(int,1),(bad,())))).
evaluate(ite,(val(bool,true),(val(int,1),(bad,())))).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,true)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(ite,(variable(x),(val(int,1),(val(string,"else"),())))).
