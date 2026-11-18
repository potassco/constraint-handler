#include "input.lp".

variable_define(result(Operator,Index),operation(Operator,(Left,(Right,())))) :-
    step(Index), Operator = (eq;neq;lt;leq;gt;geq),
    Left = operation(add,(variable(input),(val(int,Index),()))),
    Right = operation(add,(Left,(val(float,float("0.000000001")),()))).
variable_define(equal(Index),operation(eq,(Operand,(Operand,())))) :-
    step(Index), Operand = operation(add,(variable(input),(val(int,Index),()))).