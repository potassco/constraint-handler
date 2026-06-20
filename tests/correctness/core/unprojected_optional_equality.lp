% Regression for compile2 emitting multiple stable models with the same projected
% user-visible values when an optional value flows through an equality.

ensure((l1,(execution_output(x,"d"),execution_input(y,"f"))),operation(limp,(operation(hasValue,(variable(execution_output(x,"d")),())),(operation(hasValue,(variable(execution_input(y,"f")),())),())))).
ensure((l2,(a,execution_input(x,"a"))),operation(limp,(val(bool,true),(operation(eq,(variable(execution_input(x,"a")),(variable(a),()))),())))).
ensure((l4,(execution_input(x,"a"),a)),operation(limp,(val(bool,true),(operation(eq,(variable(a),(variable(execution_input(x,"a")),()))),())))).
ensure((l6,(execution_input(y,"f"),execution_output(x,"d"))),operation(limp,(operation(conj,(operation(hasValue,(variable(execution_input(y,"f")),())),(operation(hasValue,(variable(execution_output(x,"d")),())),()))),(operation(eq,(variable(execution_output(x,"d")),(variable(execution_input(y,"f")),()))),())))).

execution_declare(x,x,if(operation(eq,(variable("a"),(val(int,1),()))),assign("d",val(int,1)),noop),("a",()),("d",())).
execution_declare(y,y,seq2(assign("g",operation(hasValue,(variable("f"),()))),if(operation(lnot,(operation(disj,(variable("g"),(operation(lnot,(operation(eq,(variable("e"),(val(int,1),()))),())),()))),())),assert(val(bool,false)),noop)),("e",("f",())),()).

execution_run(x,x).
execution_run(y,y).

variable_declare(a,a,fromFacts).
variable_declare(execution_input(x,"a"),execution_input(x,"a"),fromFacts).
variable_declare(execution_input(y,"e"),execution_input(y,"e"),fromFacts).
variable_declare(execution_input(y,"f"),execution_input(y,"f"),fromFacts).
variable_declareOptional(execution_input(y,"f")).

variable_domain(a,val(int,0)).
variable_domain(a,val(int,1)).
variable_domain(execution_input(x,"a"),variable(a)).
variable_domain(execution_input(y,"e"),val(int,0)).
variable_domain(execution_input(y,"e"),val(int,1)).
variable_domain(execution_input(y,"f"),variable(execution_output(x,"d"))).
