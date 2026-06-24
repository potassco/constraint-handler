variable_define(x,python("2")).
variable_define(y,operation(sub,(variable(x),(python("3"),())))).
variable_define(z,operation(python("abs"),(variable(y),()))).

phase_request(type_check,false).
