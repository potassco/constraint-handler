phase_request(type_check,true).

typed(VAR) :- type_variable(VAR,T), T!=bot.

variable_declare(v_string,fromFacts).
variable_domain(v_string,val(string,"s")).
variable_declare(v_bool,boolDomain).
variable_declare(v_int,fromFacts).
variable_domain(v_int,val(int,1)).

variable_define(c_add_bad,operation(add,(variable(v_string),(variable(v_bool),())))).
variable_define(c_mult_bad,operation(mult,(variable(v_string),(variable(v_bool),())))).
variable_define(c_limp_bad,operation(limp,(variable(v_string),(variable(v_int),())))).
