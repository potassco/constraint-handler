phase_request(type_check,true).

variable_declare(v_int,fromFacts).
variable_domain(v_int,val(int,3)).
variable_declare(v_float,fromFacts).
variable_domain(v_float,val(float,float("3.14"))).

variable_define(c_add_0,operation(add,())).
variable_define(c_add_1,operation(add,(variable(v_int),()))).
variable_define(c_add_2,operation(add,(variable(v_int),(variable(v_int),())))).
variable_define(c_add_3,operation(add,(variable(v_int),(variable(v_int),(variable(v_int),()))))).
variable_define(c_add_4,operation(add,(variable(v_int),(variable(v_int),(variable(v_int),(variable(v_int),())))))).
variable_define(c_add_5,operation(add,(variable(v_int),(variable(v_int),(variable(v_int),(variable(v_int),(variable(v_int),()))))))).

variable_define(c_mult_0,operation(mult,())).
variable_define(c_mult_1,operation(mult,(variable(v_int),()))).
variable_define(c_mult_2,operation(mult,(variable(v_int),(variable(v_int),())))).
variable_define(c_mult_3,operation(mult,(variable(v_int),(variable(v_int),(variable(v_int),()))))).
variable_define(c_mult_4,operation(mult,(variable(v_int),(variable(v_int),(variable(v_int),(variable(v_int),())))))).
variable_define(c_mult_5,operation(mult,(variable(v_int),(variable(v_int),(variable(v_int),(variable(v_int),(variable(v_int),()))))))).

variable_define(c_add_mixed_3,operation(add,(variable(v_float),(variable(v_int),(variable(v_float),()))))).
variable_define(c_mult_mixed_4,operation(mult,(variable(v_float),(variable(v_int),(variable(v_float),(variable(v_int),())))))).
