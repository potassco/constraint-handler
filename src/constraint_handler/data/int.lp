%%%%%%%%%%%%%%%%% add mult
operator_declare_variadic(OP,T,T,1) :- T = int, OP = (add;mult).

% Variadic integer addition via aggregation over indexed argument values.
% This avoids building tail tuples of evaluated arguments.
_computedIdx_id(E_ID, val(int, N)) :-
    _computeIdx_id(E_ID, add),
    _direct_queryArgsValues_id(E_ID, add, ARGS),
    LEN = @pythonListLength(ARGS),
    LEN = #count { IDX : _computeIdx_id(E_ID, IDX, val(int, _)) },
    N = #sum { V, IDX : _computeIdx_id(E_ID, IDX, val(int, V)) }.

% Variadic integer multiplication.
% Short-circuit to 0 if any argument is 0.
_computedIdx_id(E_ID,val(int,0)) :- _computeIdx_id(E_ID,mult), _computeIdx_id(E_ID,IDX,val(int,0)).
% Empty product is 1.
_computedIdx_id(E_ID,val(int,1)) :- _computeIdx_id(E_ID,mult), not _computeIdx_id(E_ID, 0, _).
_int_mult_id(E_ID,0,val(int,1)) :- _computeIdx_id(E_ID,mult).
_int_mult_id(E_ID,IDX+1,val(int,VO*V)) :- _computeIdx_id(E_ID,mult), _computeIdx_id(E_ID,IDX,val(int,V)), _int_mult_id(E_ID,IDX,val(int,VO)).
_computedIdx_id(E_ID,V)  :- _computeIdx_id(E_ID,mult), _int_mult_id(E_ID,IDX,V), _computeIdx_id(E_ID,IDX-1,_), not _computeIdx_id(E_ID,IDX,_).

%%%%%%%%%%%%%%%%% sub int_div pow
operator_declare(OP,(T,(T,())),T) :- T = int, OP = (sub;pow).
operator_declare(OP,(T1,(T2,())),T) :- T = int, T1 = (int;float), T2 = (int;float), OP = int_div.
_computedIdx_id(E_ID,val(int,V1-V2)) :-
    _computeIdx_id(E_ID, sub),
    _computeIdx_id(E_ID, 0, val(int, V1)),
    _computeIdx_id(E_ID, 1, val(int, V2)).

_computedIdx_id(E_ID,val(int,V1/V2)) :-
    _computeIdx_id(E_ID, int_div),
    _computeIdx_id(E_ID, 0, val(int, V1)),
    _computeIdx_id(E_ID, 1, val(int, V2)),
    V2 != 0.

_computedIdx_id(E_ID,bad) :-
    _computeIdx_id(E_ID, OP),
    OP = (int_div;float_div),
    _computeIdx_id(E_ID, 1, val(int, V2)),
    V2 = 0.

warning(expression(zeroDivisionError),(),(OP,E)) :-
    _expr_id(E_ID,E),
    _computeIdx_id(E_ID, OP),
    OP = (int_div;float_div),
    _computeIdx_id(E_ID, 1, val(int, V2)),
    V2 = 0.

_computedIdx_id(E_ID,val(int,V1**V2)) :-
    _computeIdx_id(E_ID, pow),
    _computeIdx_id(E_ID, 0, val(int, V1)),
    _computeIdx_id(E_ID, 1, val(int, V2)).

%%%%%%%%%%%%%%%%% abs minus
operator_declare(OP,(T,()),T) :- T = int, OP = (abs;minus).
_computedIdx_id(E_ID,val(int,|V|)) :- _computeIdx_id(E_ID, abs), _computeIdx_id(E_ID, 0, val(int, V)).
_computedIdx_id(E_ID,val(int,-V))  :- _computeIdx_id(E_ID, minus), _computeIdx_id(E_ID, 0, val(int, V)).

%%%%%%%%%%%%%%%%% comparison
operator_declare(OP,(T,(T,())),bool) :- T = int, OP = (leq;lt;geq;gt).

% Remaining comparisons (order-based) use the concrete values.
_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, leq), _computeIdx_id(E_ID, 0, val(int, V1)), _computeIdx_id(E_ID, 1, val(int, V2)), V1 <= V2.
_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, lt),  _computeIdx_id(E_ID, 0, val(int, V1)), _computeIdx_id(E_ID, 1, val(int, V2)), V1 < V2.
_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, geq), _computeIdx_id(E_ID, 0, val(int, V1)), _computeIdx_id(E_ID, 1, val(int, V2)), V1 >= V2.
_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, gt),  _computeIdx_id(E_ID, 0, val(int, V1)), _computeIdx_id(E_ID, 1, val(int, V2)), V1 > V2.

_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, leq), _computeIdx_id(E_ID, 0, val(int, V1)), _computeIdx_id(E_ID, 1, val(int, V2)), V1 > V2.
_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, lt),  _computeIdx_id(E_ID, 0, val(int, V1)), _computeIdx_id(E_ID, 1, val(int, V2)), V1 >= V2.
_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, geq), _computeIdx_id(E_ID, 0, val(int, V1)), _computeIdx_id(E_ID, 1, val(int, V2)), V1 < V2.
_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, gt),  _computeIdx_id(E_ID, 0, val(int, V1)), _computeIdx_id(E_ID, 1, val(int, V2)), V1 <= V2.

_computedIdx_id(E_ID,val(int,V2)) :- _computeIdx_id(E_ID, max), _computeIdx_id(E_ID, 0, val(int, V1)), _computeIdx_id(E_ID, 1, val(int, V2)), V1 <= V2.
_computedIdx_id(E_ID,val(int,V1)) :- _computeIdx_id(E_ID, max), _computeIdx_id(E_ID, 0, val(int, V1)), _computeIdx_id(E_ID, 1, val(int, V2)), V1 > V2.
_computedIdx_id(E_ID,val(int,V2)) :- _computeIdx_id(E_ID, min), _computeIdx_id(E_ID, 0, val(int, V1)), _computeIdx_id(E_ID, 1, val(int, V2)), V1 > V2.
_computedIdx_id(E_ID,val(int,V1)) :- _computeIdx_id(E_ID, min), _computeIdx_id(E_ID, 0, val(int, V1)), _computeIdx_id(E_ID, 1, val(int, V2)), V1 <= V2.

_computedIdx_id(E_ID,RES) :-
    _computeIdx_id(E_ID, float_div),
    _computeIdx_id(E_ID, 0, val(int, V1)),
    _computeIdx_id(E_ID, 1, val(int, V2)),
        V2 != 0,
        ARGS = (val(int, V1), (val(int, V2), ())),
        RES = @pythonEvalExpr(operation(float_div, ARGS), (), ID),
        _main_solverIdentifier(ID).
