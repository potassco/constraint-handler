% Reproducer: compile2 goes UNSAT when an execution assigns an empty set
% and the output is linked to an optional set-valued variable.

ensure(operation(limp,(operation(conj,(variable(a),(operation(hasValue,(variable(execution_output(e,"b")),())),()))),(operation(eq,(variable(execution_output(e,"b")),(variable(b),()))),())))).

set_baseDomain(s0(b),val(string,"x")).
variable_declare(a,boolDomain).
variable_define(b,operation(if,(variable(a),(variable(s0(b)),())))).

variable_define(i,val(int,1),i).
variable_declare(execution_input(e,"a"),fromFacts).
variable_domain(execution_input(e,"a"),variable(i)).

execution_declare(e,if(operation(eq,(variable("a"),(val(int,1),()))),assign("b",operation(set_make,())),noop),("a",()),("b",())).
