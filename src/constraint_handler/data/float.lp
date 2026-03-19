intToFloatOperator(sqrt;cos;sin;tan;acos;asin;atan).
floatUnOperator(abs;sqrt;cos;sin;tan;acos;asin;atan;minus;floor).
floatFloatFloatOperator(add;sub;mult;float_div;pow;max;min).
floatBinOperator(OP) :- floatFloatFloatOperator(OP).
floatBinOperator(int_div;leq;lt;geq;gt).

operator_declare_variadic(OP,T,T,2) :- T = float, OP = (add;mult).
operator_declare(OP,(T,()),float) :- T = (int;float), intToFloatOperator(OP).
operator_declare(OP,(T,()),float) :- T = float, OP = (abs;minus).
operator_declare(OP,(T,()),int) :- T = float, OP = floor.
operator_declare(OP,(T1,(T2,())),float) :- T1 = (int;float),T2 = (int;float), (T1,T2) != (int,int), floatFloatFloatOperator(OP).
operator_declare(OP,(T,(T,())),float) :- T = int, OP = float_div.
operator_declare(OP,(T1,(T2,())),bool) :- T1 = (int;float),T2 = (int;float), (T1,T2) != (int,int), OP = (leq;lt;geq;gt).
operator_declare(OP,(T,(T,())),bool) :- T = float, OP = (eq;neq).

_float_eval_exec_id(E_ID, RES) :-
    _computeIdx_id(E_ID, OP),
    intToFloatOperator(OP),
    _computeIdx_id(E_ID, 0, val(int, V)),
    ARGS = (val(int, V), ()),
    RES = @pythonEvalExpr(operation(OP, ARGS), (), ID),
    _main_solverIdentifier(ID).

_float_eval_exec_id(E_ID, RES) :-
    _computeIdx_id(E_ID, OP),
    floatUnOperator(OP),
    _computeIdx_id(E_ID, 0, val(float, V)),
    ARGS = (val(float, V), ()),
    RES = @pythonEvalExpr(operation(OP, ARGS), (), ID),
    _main_solverIdentifier(ID).

_float_eval_exec_id(E_ID, RES) :-
    _computeIdx_id(E_ID, OP),
    floatBinOperator(OP),
    _computeIdx_id(E_ID, 0, val(T1, V1)),
    _computeIdx_id(E_ID, 1, val(T2, V2)),
    (T1;T2) = float,
    T1 = (float;int),
    T2 = (float;int),
    ARGS = (val(T1, V1), (val(T2, V2), ())),
    RES = @pythonEvalExpr(operation(OP, ARGS), (), ID),
    _main_solverIdentifier(ID).

% Float equality/inequality must be numeric (e.g., float("2") == float("2.0")).
_float_eval_exec_id(E_ID, RES) :-
    _computeIdx_id(E_ID, OP),
    OP = (eq;neq),
    _computeIdx_id(E_ID, 0, val(float, V1)),
    _computeIdx_id(E_ID, 1, val(float, V2)),
    ARGS = (val(float, V1), (val(float, V2), ())),
    RES = @pythonEvalExpr(operation(OP, ARGS), (), ID),
    _main_solverIdentifier(ID).

_float_eval_exec(E, RES) :- _expr_id(E_ID,E), _float_eval_exec_id(E_ID, RES).

_computedIdx_id(E_ID, val(TYPE, V)) :- _float_eval_exec_id(E_ID, val(TYPE, V)).
_computedIdx_id(E_ID, bad) :- _float_eval_exec_id(E_ID, error(KIND, MSG)).
_warning(KIND,(),(OP,E,MSG)) :- _expr_id(E_ID,E), _float_eval_exec_id(E_ID, error(KIND, MSG)), _computeIdx_id(E_ID, OP).
