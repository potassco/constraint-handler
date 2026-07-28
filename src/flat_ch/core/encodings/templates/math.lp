% =============================================================================
% INT
% =============================================================================

% Binary Addition
_fch_template_expr_val(ID, _fch_type_int_id, V1 + V2) :-
    _fch_op_add(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2).

% Variadic Addition
_fch_template_expr_val(ID, _fch_type_int_id, SUM) :-
    _fch_op_add_variadic(ID, LEN),
    LEN = #count { INDEX : _fch_op_add_arg(ID, INDEX, A), _fch_template_expr_val(A, _fch_type_int_id, _) },
    SUM = #sum { V, INDEX : _fch_op_add_arg(ID, INDEX, A), _fch_template_expr_val(A, _fch_type_int_id, V) }.

% Variadic Multiplication Helper
_fch_template_mult_prefix(ID, 0, 1) :-
    _fch_op_mult_variadic(ID, _).

_fch_template_mult_prefix(ID, NEXT, PRODUCT * V) :-
    _fch_template_mult_prefix(ID, INDEX, PRODUCT),
    _fch_op_mult_arg(ID, NEXT, A),
    NEXT = INDEX + 1,
    _fch_template_expr_val(A, _fch_type_int_id, V).

% Binary Subtraction
_fch_template_expr_val(ID, _fch_type_int_id, V1 - V2) :-
    _fch_op_sub(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2).

% Binary Multiplication
_fch_template_expr_val(ID, _fch_type_int_id, V1 * V2) :-
    _fch_op_mult(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2).

% Variadic Multiplication
_fch_template_expr_val(ID, _fch_type_int_id, PRODUCT) :-
    _fch_op_mult_variadic(ID, LEN),
    _fch_template_mult_prefix(ID, LEN, PRODUCT).

% Binary Integer Division
_fch_template_expr_val(ID, _fch_type_int_id, V1 / V2) :-
    _fch_op_int_div(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V2 != 0.

% Binary Power
_fch_template_expr_val(ID, _fch_type_int_id, V1 ** V2) :-
    _fch_op_pow(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2).

% Binary Max
_fch_template_expr_val(ID, _fch_type_int_id, V1) :-
    _fch_op_max(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 >= V2.

_fch_template_expr_val(ID, _fch_type_int_id, V2) :-
    _fch_op_max(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V2 > V1.

% Binary Min
_fch_template_expr_val(ID, _fch_type_int_id, V1) :-
    _fch_op_min(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 <= V2.

_fch_template_expr_val(ID, _fch_type_int_id, V2) :-
    _fch_op_min(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V2 < V1.

% Unary Minus
_fch_template_expr_val(ID, _fch_type_int_id, -V) :-
    _fch_op_minus(ID, A1),
    _fch_template_expr_val(A1, _fch_type_int_id, V).

% Unary Abs
_fch_template_expr_val(ID, _fch_type_int_id, VALUE) :-
    _fch_op_abs(ID, A1),
    _fch_template_expr_val(A1, _fch_type_int_id, VALUE),
    VALUE >= 0.

_fch_template_expr_val(ID, _fch_type_int_id, -VALUE) :-
    _fch_op_abs(ID, A1),
    _fch_template_expr_val(A1, _fch_type_int_id, VALUE),
    VALUE < 0.

% Unary Ceil / Floor
_fch_template_expr_val(ID, _fch_type_int_id, V) :-
    _fch_op_ceil(ID, A1),
    _fch_template_expr_val(A1, _fch_type_int_id, V).

_fch_template_expr_val(ID, _fch_type_int_id, V) :-
    _fch_op_floor(ID, A1),
    _fch_template_expr_val(A1, _fch_type_int_id, V).


% =============================================================================
% FLOAT & MIXED
% =============================================================================

% Ceil (Float -> Int)
_fch_template_expr_val(ID, _fch_type_int_id, INT_PART + 1) :-
    _fch_op_ceil(ID, A1),
    _fch_template_expr_val(A1, _fch_type_float_id, (INT_PART, REMAINDER)),
    REMAINDER > 0.

_fch_template_expr_val(ID, _fch_type_int_id, INT_PART) :-
    _fch_op_ceil(ID, A1),
    _fch_template_expr_val(A1, _fch_type_float_id, (INT_PART, REMAINDER)),
    REMAINDER <= 0.

% Floor (Float -> Int)
_fch_template_expr_val(ID, _fch_type_int_id, INT_PART - 1) :-
    _fch_op_floor(ID, A1),
    _fch_template_expr_val(A1, _fch_type_float_id, (INT_PART, REMAINDER)),
    REMAINDER < 0.

_fch_template_expr_val(ID, _fch_type_int_id, INT_PART) :-
    _fch_op_floor(ID, A1),
    _fch_template_expr_val(A1, _fch_type_float_id, (INT_PART, REMAINDER)),
    REMAINDER >= 0.

% Unary Minus (Float)
_fch_template_expr_val(ID, _fch_type_float_id, (-INT_PART, -REMAINDER)) :-
    _fch_op_minus(ID, A1),
    _fch_template_expr_val(A1, _fch_type_float_id, (INT_PART, REMAINDER)).

% Unary Abs (Float)
_fch_template_expr_val(ID, _fch_type_float_id, VALUE) :-
    _fch_op_abs(ID, A1),
    _fch_template_expr_val(A1, _fch_type_float_id, VALUE),
    VALUE >= (0, 0).

_fch_template_expr_val(ID, _fch_type_float_id, (-INT_PART, -REMAINDER)) :-
    _fch_op_abs(ID, A1),
    _fch_template_expr_val(A1, _fch_type_float_id, VALUE),
    VALUE = (INT_PART, REMAINDER),
    VALUE < (0, 0).

% Max (Mixed Int / Float & Float / Float)
_fch_template_expr_val(ID, _fch_type_int_id, V1) :-
    _fch_op_max(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    (V1, 0) >= V2.

_fch_template_expr_val(ID, _fch_type_float_id, V2) :-
    _fch_op_max(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    (V1, 0) < V2.

_fch_template_expr_val(ID, _fch_type_float_id, V1) :-
    _fch_op_max(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 >= (V2, 0).

_fch_template_expr_val(ID, _fch_type_int_id, V2) :-
    _fch_op_max(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 < (V2, 0).

_fch_template_expr_val(ID, _fch_type_float_id, V1) :-
    _fch_op_max(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    V1 >= V2.

_fch_template_expr_val(ID, _fch_type_float_id, V2) :-
    _fch_op_max(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    V2 > V1.

% Min (Mixed Int / Float & Float / Float)
_fch_template_expr_val(ID, _fch_type_int_id, V1) :-
    _fch_op_min(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    (V1, 0) <= V2.

_fch_template_expr_val(ID, _fch_type_float_id, V2) :-
    _fch_op_min(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    (V1, 0) > V2.

_fch_template_expr_val(ID, _fch_type_float_id, V1) :-
    _fch_op_min(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 <= (V2, 0).

_fch_template_expr_val(ID, _fch_type_int_id, V2) :-
    _fch_op_min(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2),
    V1 > (V2, 0).

_fch_template_expr_val(ID, _fch_type_float_id, V1) :-
    _fch_op_min(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    V1 <= V2.

_fch_template_expr_val(ID, _fch_type_float_id, V2) :-
    _fch_op_min(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, V1),
    _fch_template_expr_val(A2, _fch_type_float_id, V2),
    V2 < V1.


% =============================================================================
% FLOAT ARITHMETIC
% =============================================================================

_fch_template_expr_val(ID, _fch_type_float_id, (I1 + I2 + 1, R1 + R2 - _fch_float_remainder_scale)) :-
    _fch_op_add(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, (I1, R1)),
    _fch_template_expr_val(A2, _fch_type_float_id, (I2, R2)),
    R1 + R2 >= _fch_float_remainder_scale.

_fch_template_expr_val(ID, _fch_type_float_id, (I1 + I2 - 1, R1 + R2 + _fch_float_remainder_scale)) :-
    _fch_op_add(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, (I1, R1)),
    _fch_template_expr_val(A2, _fch_type_float_id, (I2, R2)),
    R1 + R2 <= -_fch_float_remainder_scale.

_fch_template_expr_val(ID, _fch_type_float_id, (I1 + I2, R1 + R2)) :-
    _fch_op_add(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, (I1, R1)),
    _fch_template_expr_val(A2, _fch_type_float_id, (I2, R2)),
    R1 + R2 < _fch_float_remainder_scale,
    R1 + R2 > -_fch_float_remainder_scale.

_fch_template_expr_val(ID, _fch_type_float_id, (I1 + I2, R1)) :-
    _fch_op_add(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, (I1, R1)),
    _fch_template_expr_val(A2, _fch_type_int_id, I2).

_fch_template_expr_val(ID, _fch_type_float_id, (I1 + I2, R2)) :-
    _fch_op_add(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, I1),
    _fch_template_expr_val(A2, _fch_type_float_id, (I2, R2)).

_fch_template_expr_val(ID, _fch_type_float_id, (I1 - I2 + 1, R1 - R2 - _fch_float_remainder_scale)) :-
    _fch_op_sub(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, (I1, R1)),
    _fch_template_expr_val(A2, _fch_type_float_id, (I2, R2)),
    R1 - R2 >= _fch_float_remainder_scale.

_fch_template_expr_val(ID, _fch_type_float_id, (I1 - I2 - 1, R1 - R2 + _fch_float_remainder_scale)) :-
    _fch_op_sub(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, (I1, R1)),
    _fch_template_expr_val(A2, _fch_type_float_id, (I2, R2)),
    R1 - R2 <= -_fch_float_remainder_scale.

_fch_template_expr_val(ID, _fch_type_float_id, (I1 - I2, R1 - R2)) :-
    _fch_op_sub(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, (I1, R1)),
    _fch_template_expr_val(A2, _fch_type_float_id, (I2, R2)),
    R1 - R2 < _fch_float_remainder_scale,
    R1 - R2 > -_fch_float_remainder_scale.

_fch_template_expr_val(ID, _fch_type_float_id, (I1 - I2, R1)) :-
    _fch_op_sub(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_float_id, (I1, R1)),
    _fch_template_expr_val(A2, _fch_type_int_id, I2).

_fch_template_expr_val(ID, _fch_type_float_id, (I1 - I2, -R2)) :-
    _fch_op_sub(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, I1),
    _fch_template_expr_val(A2, _fch_type_float_id, (I2, R2)).

% @expand float_numeric_pairs
_fch_template_python_binary(ID, _fch_op_mult_id, (({{LEFT_TYPE}}, V1), ({{RIGHT_TYPE}}, V2))) :-
    _fch_op_mult(ID, A1, A2),
    _fch_template_expr_val(A1, {{LEFT_TYPE}}, V1),
    _fch_template_expr_val(A2, {{RIGHT_TYPE}}, V2).
% @endexpand

% @expand float_numeric_pairs
_fch_template_python_binary(ID, _fch_op_int_div_id, (({{LEFT_TYPE}}, V1), ({{RIGHT_TYPE}}, V2))) :-
    _fch_op_int_div(ID, A1, A2),
    _fch_template_expr_val(A1, {{LEFT_TYPE}}, V1),
    _fch_template_expr_val(A2, {{RIGHT_TYPE}}, V2).
% @endexpand

% @expand float_numeric_pairs
_fch_template_python_binary(ID, _fch_op_float_div_id, (({{LEFT_TYPE}}, V1), ({{RIGHT_TYPE}}, V2))) :-
    _fch_op_float_div(ID, A1, A2),
    _fch_template_expr_val(A1, {{LEFT_TYPE}}, V1),
    _fch_template_expr_val(A2, {{RIGHT_TYPE}}, V2).
% @endexpand

_fch_template_python_binary(ID, _fch_op_float_div_id, ((_fch_type_int_id, V1), (_fch_type_int_id, V2))) :-
    _fch_op_float_div(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_int_id, V1),
    _fch_template_expr_val(A2, _fch_type_int_id, V2).

% @expand float_numeric_pairs
_fch_template_python_binary(ID, _fch_op_pow_id, (({{LEFT_TYPE}}, V1), ({{RIGHT_TYPE}}, V2))) :-
    _fch_op_pow(ID, A1, A2),
    _fch_template_expr_val(A1, {{LEFT_TYPE}}, V1),
    _fch_template_expr_val(A2, {{RIGHT_TYPE}}, V2).
% @endexpand

_fch_template_python_unary(ID, _fch_op_sqrt_id, ((T, V),)) :-
    _fch_op_sqrt(ID, A1),
    _fch_template_expr_val(A1, T, V).

_fch_template_python_unary(ID, _fch_op_length_id, ((_fch_type_string_id, V),)) :-
    _fch_op_length(ID, A1),
    _fch_template_expr_val(A1, _fch_type_string_id, V).

_fch_template_python_binary(ID, _fch_op_concat_id, ((_fch_type_string_id, V1), (_fch_type_string_id, V2))) :-
    _fch_op_concat(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_string_id, V1),
    _fch_template_expr_val(A2, _fch_type_string_id, V2).


_fch_template_expr_val(ID, _fch_type_float_id, (V, 0)) :-
    _fch_op_float_from_int(ID, A),
    _fch_template_expr_val(A1, _fch_type_int_id, V).

_fch_template_expr_val(ID, _fch_type_int_id, V) :-
    _fch_op_int_from_float(ID, A),
    _fch_template_expr_val(A1, _fch_type_float_id, (V, _)).
