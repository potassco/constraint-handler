#include "input.lp".

variable_define(squared(Index),operation(mult,(Root,(Root,())))) :-
	step(Index),
	Argument = operation(add,(variable(input),(val(int,Index),()))),
	Root = operation(sqrt,(Argument,())).