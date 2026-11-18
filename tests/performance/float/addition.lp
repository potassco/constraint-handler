#include "input.lp".

variable_define(result(0),variable(input)).
variable_define(result(I),operation(add,(variable(result(I-1)),(val(float,float("0.125")),())))) :- step(I).