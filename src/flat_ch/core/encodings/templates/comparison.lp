% =============================================================================
% INT
% =============================================================================

% Less than or Equal
_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_leq(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 <= V2.

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_leq(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 > V2.

% Less Than
_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_lt(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 < V2.

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_lt(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 >= V2.

% Greater Than
_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_gt(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 > V2.

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_gt(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 <= V2.

% Greater than or Equal
_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_geq(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 >= V2.

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_geq(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 < V2.

% =============================================================================
% FLOATS & MIXED
% =============================================================================

% Less than or Equal
_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_leq(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    (V1, 0) <= V2.

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_leq(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    (V1, 0) > V2.

_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_leq(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 <= (V2, 0).

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_leq(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 > (V2, 0).

_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_leq(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    V1 <= V2.

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_leq(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    V1 > V2.

% Less Than
_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_lt(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    (V1, 0) < V2.

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_lt(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    (V1, 0) >= V2.

_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_lt(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 < (V2, 0).

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_lt(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 >= (V2, 0).

_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_lt(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    V1 < V2.

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_lt(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    V1 >= V2.

% Greater Than
_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_gt(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    (V1, 0) > V2.

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_gt(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    (V1, 0) <= V2.

_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_gt(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 > (V2, 0).

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_gt(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 <= (V2, 0).

_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_gt(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    V1 > V2.

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_gt(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    V1 <= V2.

% Greater than or Equal
_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_geq(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    (V1, 0) >= V2.

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_geq(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    (V1, 0) < V2.

_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_geq(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 >= (V2, 0).

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_geq(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 < (V2, 0).

_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_geq(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    V1 >= V2.

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_geq(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    V1 < V2.
