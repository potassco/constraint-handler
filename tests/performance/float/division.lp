#include "input.lp".

variable_define(recovered(Index),operation(mult,(Quotient,(val(int,30),())))) :-
	step(Index),
	Numerator = operation(add,(variable(input),(val(int,Index),()))),
	Quotient = operation(float_div,(Numerator,(val(int,30),()))).