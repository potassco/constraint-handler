% Regression for compile2 emitting multiple stable models when two hidden
% comparisons are evaluated on an absent optional value.

ensure((absent,prop),operation(eq,(operation(hasValue,(variable(prop),())),(val(bool,false),())))).
bool_evaluate(operation(lt,(variable(prop),(val(int,3),())))).
bool_evaluate(operation(geq,(variable(prop),(val(int,3),())))).

variable_declare(prop,prop,fromFacts).
variable_domain(prop,val(none,none)).
variable_domain(prop,val(int,5)).
