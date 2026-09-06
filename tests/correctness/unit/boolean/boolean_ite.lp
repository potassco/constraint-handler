evaluate(operation(ite,(val(bool,true),(val(int,1),(val(string,"else"),()))))).
evaluate(operation(ite,(val(bool,false),(val(int,1),(val(string,"else"),()))))).
evaluate(operation(ite,(val(none,none),(val(int,1),(val(string,"else"),()))))).
evaluate(operation(ite,(bad,(val(int,1),(val(string,"else"),()))))).
evaluate(operation(ite,(val(bool,true),(bad,(val(string,"else"),()))))).
evaluate(operation(ite,(val(bool,false),(bad,(val(string,"else"),()))))).
evaluate(operation(ite,(val(bool,false),(val(int,1),(bad,()))))).
evaluate(operation(ite,(val(bool,true),(val(int,1),(bad,()))))).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,true)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(ite,(variable(x),(val(int,1),(val(string,"else"),()))))).
