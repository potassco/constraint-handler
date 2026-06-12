%%% declare empty
%%% set_fold(+,empty,0) = 0

%%% numbers = { -2.0, -1, 0, 1, 2 }
%%% squares = { x*x | x \in numbers, x float or x int } = { 0, 1, 4 }
%%% csquares = |squares| = 3

%%% isquares = { x*x | x \in numbers, x int } = { 0, 1, 4 }
%%% |isquares| = 3
%%% set_fold(+,isquares,0) = 5
%%% set_fold(*,isquares,1) = 0

variable_declare(empty,set).
evaluate(set_fold,(val(function,add),(variable(empty),(val(int,0),())))).

variable_define(numbers, operation(set_make,
                                    (val(float,float("-2.0")),
                                    (val(int,-1),
                                    (val(int, 0),
                                    (val(int, 1),
                                    (val(int, 2),()))))))).

variable_declare(squares,set).
set_assign(squares, SQ) :-
    set_value(numbers,EX),
    SQ = operation(mult,(EX,(EX,()))),
    EX = val(T,X).

variable_define(csquares, operation(length,(variable(squares),()))).

variable_declare(isquares,set).
set_assign(isquares, SQ) :-
    set_value(numbers,EX),
    SQ = operation(mult,(EX,(EX,()))),
    EX = val(int,X).

evaluate(length,(variable(isquares),())).
evaluate(set_fold,(val(function,add),(variable(isquares),(val(int,0),())))).
evaluate(set_fold,(val(function,mult),(variable(isquares),(val(int,1),())))).
