#include "input.lp".

variable_define(result(Index),operation(add,(SineSquared,(CosineSquared,())))) :-
	step(Index),
	Angle = operation(add,(variable(input),(val(int,Index),()))),
	Sine = operation(sin,(Angle,())),
	Cosine = operation(cos,(Angle,())),
	SineSquared = operation(mult,(Sine,(Sine,()))),
	CosineSquared = operation(mult,(Cosine,(Cosine,()))).
