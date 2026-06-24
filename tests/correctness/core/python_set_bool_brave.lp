% Regression extracted from Kroco brave reasoning.
% Compile reaches the non-empty-set branch; compile2 does not.

ensure(operation(limp,(val(bool,true),(operation(eq,(variable(execution_input(q,"c")),(variable(execution_output(p,"c")),()))),())))).
ensure(operation(limp,(val(bool,true),(operation(eq,(variable(execution_input(q,"b")),(variable(b),()))),())))).
ensure(operation(limp,(val(bool,true),(operation(eq,(variable(execution_input(p,"a")),(variable(a),()))),())))).

execution_run(p).
execution_run(q).

set_declare(a,a).
variable_domain(b,val(int,2)).
variable_domain(b,val(int,1)).
variable_domain(execution_input(p,"a"),variable(a)).
variable_domain(execution_input(q,"c"),variable(execution_output(p,"c"))).
variable_domain(execution_input(q,"b"),variable(b)).

set_baseDomain(a,a,val(string,"x")).

execution_declare(p,statement_python("c = set(a) == set([])"),("a",()),("c",())).
execution_declare(q,assert(operation(eq,(variable("c"),(operation(eq,(variable("b"),(val(int,1),()))),())))),("b",("c",())),()).

evaluate(eq,(variable(b),(val(int,2),()))).
