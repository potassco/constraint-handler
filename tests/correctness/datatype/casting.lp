variable_declare(ix,fromFacts).
variable_domain(ix,val(int,3)).

variable_define(fy,val(float,float("5.0"))).

variable_define(fx,operation(float_from_int,(variable(ix),()))).
variable_define(iy,operation(int_from_float,(variable(fy),()))).
