% Preserved larger version of the compile2 duplicate-model regression.

variable_declare(a,fromFacts).
variable_domain(a,val(string,"l")).
variable_domain(a,val(string,"r")).

variable_declare(b,boolDomain).
variable_declare(c,boolDomain).
ensure(operation(eq,(variable(b),(operation(eq,(variable(a),(val(string,"l"),()))),())))).
ensure(operation(eq,(variable(c),(operation(eq,(variable(a),(val(string,"r"),()))),())))).

variable_declare(d,fromFacts).
variable_declareOptional(d).
variable_declare(e,fromFacts).
variable_declareOptional(e).
variable_declare(f,fromFacts).

ensure(operation(eq,(operation(hasValue,(variable(d),())),(variable(b),())))).
ensure(operation(eq,(operation(hasValue,(variable(e),())),(variable(c),())))).
ensure(operation(hasValue,(variable(f),()))).

ensure(operation(limp,(variable(b),(operation(eq,(variable(execution_output(p,"x")),(variable(d),()))),())))).
ensure(operation(limp,(variable(b),(operation(eq,(variable(d),(variable(execution_output(p,"x")),()))),())))).
ensure(operation(limp,(variable(b),(operation(eq,(variable(d),(variable(f),()))),())))).

ensure(operation(limp,(variable(c),(operation(eq,(variable(execution_output(q,"y")),(variable(e),()))),())))).
ensure(operation(limp,(variable(c),(operation(eq,(variable(e),(variable(execution_output(q,"y")),()))),())))).
ensure(operation(limp,(variable(c),(operation(eq,(variable(e),(variable(f),()))),())))).

variable_domain(d,variable(execution_output(p,"x"))).
variable_domain(d,variable(execution_output(q,"y"))).
variable_domain(e,variable(execution_output(q,"y"))).
variable_domain(e,variable(execution_output(p,"x"))).
variable_domain(f,variable(execution_output(p,"x"))).
variable_domain(f,variable(execution_output(q,"y"))).

variable_define(execution_input(p,run),variable(b)).
variable_define(execution_input(q,run),variable(c)).

execution_declare(p,if(variable(run),assign("x",val(float,float("1.1"))),noop),(run,()),("x",())).
execution_declare(q,if(variable(run),assign("y",val(float,float("2.2"))),noop),(run,()),("y",())).
execution_run(p).
execution_run(q).

evaluate(eq,(variable(f),(val(float,float("1.1")),()))).
evaluate(eq,(variable(f),(val(float,float("2.2")),()))).
evaluate(disj,(operation(eq,(variable(f),(val(float,float("1.1")),()))),(operation(eq,(variable(f),(val(float,float("2.2")),()))),()))).
