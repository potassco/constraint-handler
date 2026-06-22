% Reproducer: compile2 goes UNSAT when an execution assigns an empty set
% and the output is linked to an optional set-valued variable.

ensure((c,(b,execution_output(e,"b"))),operation(limp,(operation(conj,(variable(a),(operation(hasValue,(variable(execution_output(e,"b")),())),()))),(operation(eq,(variable(execution_output(e,"b")),(variable(b),()))),())))).

set_baseDomain(b,s0(b),val(string,"x")).
variable_declare(a,a,boolDomain).
variable_define(b,b,operation(if,(variable(a),(variable(s0(b)),())))).

variable_define(i,i,val(int,1)).
variable_declare(execution_input(e,"a"),execution_input(e,"a"),fromFacts).
variable_domain(execution_input(e,"a"),variable(i)).

execution_declare(e,e,if(operation(eq,(variable("a"),(val(int,1),()))),assign("b",operation(set_make,())),noop),("a",()),("b",())).
