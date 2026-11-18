#include "input.lp".

variable_define(result(0),variable(input)).
variable_define(shifted(I),operation(add,(variable(result(I-1)),(val(int,1048576),())))) :- step(I).
variable_define(result(I),operation(sub,(variable(shifted(I)),(val(int,1048576),())))) :- step(I).