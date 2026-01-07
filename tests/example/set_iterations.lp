#include "includeAll.lp".


%%% declare empty
%%% set_fold(+,empty,0) = 0

%%% numbers = { -2.0, -1, 0, 1, 2 }
%%% squares = { x*x | x \in numbers, x float or x int } = { 0, 1, 4, 4.0 }
%%% csquares = |squares| = 4

%%% isquares = { x*x | x \in numbers, x int } = { 0, 1, 4 }
%%% |isquares| = 3
%%% set_fold(+,isquares,0) = 5
%%% set_fold(*,isquares,1) = 0

set_declare(d_empty,empty).
evaluate(set_fold,(val(function,add),(variable(empty),(val(int,0),())))).

variable_define(a_numbers, numbers, operation(makeSet,
                                    (val(float,float("-2.0")),
                                    (val(int,-1),
                                    (val(int, 0),
                                    (val(int, 1),
                                    (val(int, 2),()))))))).

set_declare(d_squares,squares).
set_assign(a_squares, squares, SQ) :-
    set_value(numbers,EX),
    SQ = operation(mult,(EX,(EX,()))),
    EX = val(T,X).

variable_define(a_csq, csquares, operation(length,(variable(squares),()))).

set_declare(d_squares,isquares).
set_assign(a_squares, isquares, SQ) :-
    set_value(numbers,EX),
    SQ = operation(mult,(EX,(EX,()))),
    EX = val(int,X).

evaluate(length,(variable(isquares),())).
evaluate(set_fold,(val(function,add),(variable(isquares),(val(int,0),())))).
evaluate(set_fold,(val(function,mult),(variable(isquares),(val(int,1),())))).
