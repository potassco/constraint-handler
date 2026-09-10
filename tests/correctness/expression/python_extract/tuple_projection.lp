% Regression for compile2 emitting duplicate stable models when Python-extract
% argument tuples are left unconstrained and only differ in hidden tuple values.

ensure(operation(eq,(variable(x),(val(int,1),()))),fix_x).
ensure(operation(eq,(variable(y),(val(int,0),()))),fix_y).
ensure(operation(limp,(val(bool,true),(operation(eq,(variable(x),(variable(execution_input(c,"x")),()))),()))),link_x).
ensure(operation(limp,(val(bool,true),(operation(eq,(variable(y),(variable(execution_input(c,"y")),()))),()))),link_y).
ensure(operation(limp,(operation(hasValue,(variable(y),())),(operation(hasValue,(variable(execution_input(c,"y")),())),()))),link_y_has).

execution_declare(c,statement_python("tmp = 0"),("x",("y",())),()).
execution_run(c).

variable_declare(x,fromFacts).
variable_declare(y,fromFacts).
variable_domain(y,val(none,none)).
variable_declare(execution_input(c,"x"),fromFacts).
variable_declare(execution_input(c,"y"),fromFacts).
variable_domain(execution_input(c,"y"),val(none,none)).

variable_domain(x,val(int,0)).
variable_domain(x,val(int,1)).
variable_domain(x,val(int,2)).
variable_domain(y,val(int,0)).
variable_domain(y,val(int,1)).
variable_domain(y,val(int,2)).
variable_domain(execution_input(c,"x"),variable(x)).
variable_domain(execution_input(c,"y"),variable(y)).

#show value/2.
phase_request(type_check,false).
