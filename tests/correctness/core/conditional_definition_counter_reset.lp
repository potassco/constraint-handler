variable_declare(a,boolDomain).
variable_declare(b,boolDomain).
bool_evaluate(variable(a)).
bool_evaluate(variable(b)).
:- bool_evaluated(variable(a),val(bool,true)), bool_evaluated(variable(b),val(bool,true)).
variable_define(y,val(int,1),variable(a)).
variable_define(y,val(int,2),variable(b)).
variable_define(z,operation(add,(variable(y),(val(int,1),())))).
variable_define(t,val(int,10),operation(eq,(variable(z),(val(int,2),())))).
