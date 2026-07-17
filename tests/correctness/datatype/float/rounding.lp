%%% f0 = floor(5) f2 = floor(5.2) f6 = floor(5.6)
%%% c0 = ceil(5)  c2 = ceil(5.2)  c6 = ceil(5.6)

variable_define(y,val(float,float("2.5"))).

evaluate(python("int"),(variable(y),())).

variable_define(f0,operation(floor,(val(float,float("5")),()))).
variable_define(f6,operation(floor,(val(float,float("5.2")),()))).
variable_define(f2,operation(floor,(val(float,float("5.6")),()))).

variable_define(c0,operation(ceil,(val(float,float("5")),()))).
variable_define(c2,operation(ceil,(val(float,float("5.2")),()))).
variable_define(c6,operation(ceil,(val(float,float("5.6")),()))).
