% Regression for compile2: an execution-constrained presence flag plus
% an empty set execution output currently goes UNSAT, while compile works.

ensure((h,(b,a)),operation(eq,(operation(hasValue,(variable(b),())),(variable(a),())))).

variable_declare(a,a,boolDomain).
set_declare(b,s0(b)).
set_baseDomain(b,s0(b),val(string,"x")).
variable_define(b,b,operation(if,(variable(a),(variable(s0(b)),())))).

execution_run(c,c).
variable_declare(execution_input(c,"a"),execution_input(c,"a"),fromFacts).
variable_domain(execution_input(c,"a"),variable(a)).
execution_declare(c,c,if(operation(lnot,(operation(eq,(variable("a"),(val(bool,true),()))),())),assert(val(bool,false)),noop),("a",()),()).

execution_run(d,d).
execution_declare(d,d,assign("b",operation(set_make,())),(),("b",())).

evaluate(eq,(variable(a),(val(bool,true),()))).
evaluate(hasValue,(variable(b),())).
evaluate(eq,(variable(b),(operation(set_make,()),()))).
evaluate(eq,(variable(execution_output(d,"b")),(operation(set_make,()),()))).
