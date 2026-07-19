phase_request(type_check,true).

typed(VAR) :- type_variable(VAR,T), T!=bot.

variable_declare(v_int,fromFacts).
variable_domain(v_int,val(int,3)).
variable_declare(v_float,fromFacts).
variable_domain(v_float,val(float,float("3.14"))).
variable_declare(v_string,fromFacts).
variable_domain(v_string,val(string,"s")).
variable_declare(v_bool,boolDomain).

variable_define(check(add,non_numeric),operation(add,(variable(v_string),(variable(v_bool),())))).
variable_define(check(mult,non_numeric),operation(mult,(variable(v_string),(variable(v_bool),())))).
variable_define(check(limp,non_none_bool),operation(limp,(variable(v_string),(variable(v_int),())))).

variable_define(check(int_div,float),operation(int_div,(variable(v_float),(variable(v_int),())))).
variable_define(check(float_div,int),operation(float_div,(variable(v_int),(variable(v_int),())))).

variable_define(check(leq,float),operation(leq,(variable(v_float),(variable(v_int),())))).
variable_define(check(lt,float),operation(lt,(variable(v_float),(variable(v_int),())))).
variable_define(check(geq,float),operation(geq,(variable(v_float),(variable(v_int),())))).
variable_define(check(gt,float),operation(gt,(variable(v_float),(variable(v_int),())))).
variable_define(check(eq,float),operation(eq,(variable(v_float),(variable(v_int),())))).
variable_define(check(neq,float),operation(neq,(variable(v_float),(variable(v_int),())))).
variable_define(check(leq,int),operation(leq,(variable(v_int),(variable(v_int),())))).
variable_define(check(lt,int),operation(lt,(variable(v_int),(variable(v_int),())))).
variable_define(check(geq,int),operation(geq,(variable(v_int),(variable(v_int),())))).
variable_define(check(gt,int),operation(gt,(variable(v_int),(variable(v_int),())))).
variable_define(check(eq,int),operation(eq,(variable(v_int),(variable(v_int),())))).
variable_define(check(neq,int),operation(neq,(variable(v_int),(variable(v_int),())))).

variable_define(check(floor,float),operation(floor,(variable(v_float),()))).
