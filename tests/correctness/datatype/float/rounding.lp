%%% floor/ceil checks plus python int conversion
%%% f0 = floor(5)   f2 = floor(5.2)   f6 = floor(5.6)
%%% c0 = ceil(5)    c2 = ceil(5.2)    c6 = ceil(5.6)

variable_define(y,val(float,float("2.5"))).

evaluate(python("int"),(variable(y),())).
