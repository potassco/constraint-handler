% Tuple equality should respect expression-level semantics for tuples with different arity.

variable_define(short,(val(int,1),val(int,2))).
variable_define(long,(val(int,1),val(int,2),val(int,3))).

evaluate(operation(eq,(variable(short),(variable(long),())))).
evaluate(operation(neq,(variable(short),(variable(long),())))).
phase_request(type_check,false).
