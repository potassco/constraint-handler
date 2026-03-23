%%%%%%%%%%%%%%%%% add mult
operator_declare_variadic(OP,T,T,1) :- T = int, OP = (add;mult).

% Variadic integer addition via aggregation over indexed argument values.
% This avoids building tail tuples of evaluated arguments.
_computedIdx(E, val(int, N)) :-
    _computeIdx(E, add),
    _length(E, LEN),
    LEN = #count { IDX : _computeIdx(E, IDX, val(int, _)) },
    N = #sum { V, IDX : _computeIdx(E, IDX, val(int, V)) }.

% Variadic integer multiplication.
% Short-circuit to 0 if any argument is 0.
_computedIdx(E,val(int,0)) :- _computeIdx(E,mult), _computeIdx(E,IDX,val(int,0)).
% Empty product is 1.
_computedIdx(E,val(int,1)) :- _computeIdx(E,mult), _length(E,0).
_int_mult(E,0,val(int,V)) :- _computeIdx(E,mult), _computeIdx(E,0,val(int,V)).
_int_mult(E,IDX,val(int,VO*V)) :-
    _computeIdx(E,mult),
    IDX > 0,
    _computeIdx(E,IDX,val(int,V)),
    _int_mult(E,IDX-1,val(int,VO)).
_computedIdx(E,V)  :- _computeIdx(E,mult), _length(E,LEN), LEN > 0, LAST = LEN - 1, _int_mult(E,LAST,V).

%%%%%%%%%%%%%%%%% sub int_div pow
operator_declare(OP,(T,(T,())),T) :- T = int, OP = (sub;pow).
operator_declare(OP,(T1,(T2,())),T) :- T = int, T1 = (int;float), T2 = (int;float), OP = int_div.
_computedIdx(E,val(int,V1-V2)) :-
    _computeIdx(E, sub),
    _computeIdx(E, 0, val(int, V1)),
    _computeIdx(E, 1, val(int, V2)).

_computedIdx(E,val(int,V1/V2)) :-
    _computeIdx(E, int_div),
    _computeIdx(E, 0, val(int, V1)),
    _computeIdx(E, 1, val(int, V2)),
    V2 != 0.

_computedIdx(E,bad) :-
    _computeIdx(E, OP),
    OP = (int_div;float_div),
    _computeIdx(E, 1, val(int, V2)),
    V2 = 0.

warning(expression(zeroDivisionError),(),(OP,E)) :-
    _computeIdx(E, OP),
    OP = (int_div;float_div),
    _computeIdx(E, 1, val(int, V2)),
    V2 = 0.

_computedIdx(E,val(int,V1**V2)) :-
    _computeIdx(E, pow),
    _computeIdx(E, 0, val(int, V1)),
    _computeIdx(E, 1, val(int, V2)).

%%%%%%%%%%%%%%%%% abs minus
operator_declare(OP,(T,()),T) :- T = int, OP = (abs;minus).
_computedIdx(E,val(int,|V|)) :- _computeIdx(E, abs), _computeIdx(E, 0, val(int, V)).
_computedIdx(E,val(int,-V))  :- _computeIdx(E, minus), _computeIdx(E, 0, val(int, V)).

%%%%%%%%%%%%%%%%% comparison
operator_declare(OP,(T,(T,())),bool) :- T = int, OP = (leq;lt;geq;gt).

% Remaining comparisons (order-based) use the concrete values.
_computedIdx(E,val(bool,true)) :- _computeIdx(E, leq), _computeIdx(E, 0, val(int, V1)), _computeIdx(E, 1, val(int, V2)), V1 <= V2.
_computedIdx(E,val(bool,true)) :- _computeIdx(E, lt),  _computeIdx(E, 0, val(int, V1)), _computeIdx(E, 1, val(int, V2)), V1 < V2.
_computedIdx(E,val(bool,true)) :- _computeIdx(E, geq), _computeIdx(E, 0, val(int, V1)), _computeIdx(E, 1, val(int, V2)), V1 >= V2.
_computedIdx(E,val(bool,true)) :- _computeIdx(E, gt),  _computeIdx(E, 0, val(int, V1)), _computeIdx(E, 1, val(int, V2)), V1 > V2.

_computedIdx(E,val(bool,false)) :- _computeIdx(E, leq), _computeIdx(E, 0, val(int, V1)), _computeIdx(E, 1, val(int, V2)), V1 > V2.
_computedIdx(E,val(bool,false)) :- _computeIdx(E, lt),  _computeIdx(E, 0, val(int, V1)), _computeIdx(E, 1, val(int, V2)), V1 >= V2.
_computedIdx(E,val(bool,false)) :- _computeIdx(E, geq), _computeIdx(E, 0, val(int, V1)), _computeIdx(E, 1, val(int, V2)), V1 < V2.
_computedIdx(E,val(bool,false)) :- _computeIdx(E, gt),  _computeIdx(E, 0, val(int, V1)), _computeIdx(E, 1, val(int, V2)), V1 <= V2.

_computedIdx(E,val(int,V2)) :- _computeIdx(E, max), _computeIdx(E, 0, val(int, V1)), _computeIdx(E, 1, val(int, V2)), V1 <= V2.
_computedIdx(E,val(int,V1)) :- _computeIdx(E, max), _computeIdx(E, 0, val(int, V1)), _computeIdx(E, 1, val(int, V2)), V1 > V2.
_computedIdx(E,val(int,V2)) :- _computeIdx(E, min), _computeIdx(E, 0, val(int, V1)), _computeIdx(E, 1, val(int, V2)), V1 > V2.
_computedIdx(E,val(int,V1)) :- _computeIdx(E, min), _computeIdx(E, 0, val(int, V1)), _computeIdx(E, 1, val(int, V2)), V1 <= V2.

_computedIdx(E,RES) :-
        _computeIdx(E, float_div),
        _computeIdx(E, 0, val(int, V1)),
        _computeIdx(E, 1, val(int, V2)),
        V2 != 0,
        ARGS = (val(int, V1), (val(int, V2), ())),
        RES = @pythonEvalExpr(operation(float_div, ARGS), (), ID),
        _main_solverIdentifier(ID).
