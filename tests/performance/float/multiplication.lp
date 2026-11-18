#include "input.lp".

variable_define(fractional(Index),operation(mult,(Product,(val(float,float("1.125")),())))) :-
	step(Index), Product = operation(mult,(variable(input),(val(int,Index),()))).