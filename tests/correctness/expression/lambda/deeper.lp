variable_define(x,val(int,9)).

expr(V,operation(float_div,(variable(INPUT_A),(val(int,2),())))) :-
    V = (1;2),
    (INPUT_A,V) = ((a,1);(x,2)).

variable_define(y,E) :- expr(2,E).
variable_define(z,OPER) :- LAM = lambda((a,()),E), OPER=operation(LAM,(variable(x),())), expr(1,E).


expr2(V,operation(add,(operation(float_div,(variable(INPUT_A),(val(int,2),()))),(val(int,1),())))) :-
    V = (1;2),
    (INPUT_A,V) = ((a,1);(x,2)).

variable_define(y2,E) :- expr2(2,E).
variable_define(z2,OPER) :- LAM = lambda((a,()),E), OPER=operation(LAM,(variable(x),())), expr2(1,E).
