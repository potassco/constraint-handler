% Regression: compile2 duplicates models when one variable shares two mutually
% exclusive execution outputs as its domain.

variable_declare(b,boolDomain).

variable_declare(f,fromFacts).
ensure(operation(hasValue,(variable(f),()))).
ensure(operation(limp,(variable(b),(operation(eq,(variable(execution_output(p,"x")),(variable(f),()))),())))).
ensure(operation(limp,(operation(lnot,(variable(b),())),(operation(eq,(variable(execution_output(q,"y")),(variable(f),()))),())))).

variable_domain(f,variable(execution_output(p,"x"))).
variable_domain(f,variable(execution_output(q,"y"))).

variable_define(execution_input(p,run),variable(b)).
variable_define(execution_input(q,run),operation(lnot,(variable(b),()))).

execution_declare(p,if(variable(run),assign("x",val(float,float("1.1"))),noop),(run,()),("x",())).
execution_declare(q,if(variable(run),assign("y",val(float,float("2.2"))),noop),(run,()),("y",())).
execution_run(p).
execution_run(q).

evaluate(disj,(operation(eq,(variable(f),(val(float,float("1.1")),()))),(operation(eq,(variable(f),(val(float,float("2.2")),()))),()))).
