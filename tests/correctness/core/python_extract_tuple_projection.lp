% Regression for compile2 emitting duplicate stable models when Python-extract
% argument tuples are left unconstrained and only differ in hidden tuple values.

ensure((fix_x,x),operation(eq,(variable(x),(val(int,1),())))).
ensure((fix_y,y),operation(eq,(variable(y),(val(int,0),())))).
ensure((link_x,(execution_input(c,"x"),x)),operation(limp,(val(bool,true),(operation(eq,(variable(x),(variable(execution_input(c,"x")),()))),())))).
ensure((link_y,(execution_input(c,"y"),y)),operation(limp,(val(bool,true),(operation(eq,(variable(y),(variable(execution_input(c,"y")),()))),())))).
ensure((link_y_has,(y,execution_input(c,"y"))),operation(limp,(operation(hasValue,(variable(y),())),(operation(hasValue,(variable(execution_input(c,"y")),())),())))).

execution_declare(c,c,statement_python("tmp = 0"),("x",("y",())),()).
execution_run(c,c).

variable_declare(x,x,fromFacts).
variable_declare(y,y,fromFacts).
variable_declareOptional(y).
variable_declare(execution_input(c,"x"),execution_input(c,"x"),fromFacts).
variable_declare(execution_input(c,"y"),execution_input(c,"y"),fromFacts).
variable_declareOptional(execution_input(c,"y")).

variable_domain(x,val(int,0)).
variable_domain(x,val(int,1)).
variable_domain(x,val(int,2)).
variable_domain(y,val(int,0)).
variable_domain(y,val(int,1)).
variable_domain(y,val(int,2)).
variable_domain(execution_input(c,"x"),variable(x)).
variable_domain(execution_input(c,"y"),variable(y)).

#show value/2.
