% =============================================================================
% TRIVIAL IDENTICAL REFERENCE
% =============================================================================

_fch_template_eq_left_val(ID, TYPE, VAL) :-
    _fch_op_eq(ID, A1, _),
    _fch_template_expr_val(A1, TYPE, VAL).

_fch_template_eq_right_val(ID, TYPE, VAL) :-
    _fch_op_eq(ID, _, A2),
    _fch_template_expr_val(A2, TYPE, VAL).

_fch_template_neq_left_val(ID, TYPE, VAL) :-
    _fch_op_neq(ID, A1, _),
    _fch_template_expr_val(A1, TYPE, VAL).

_fch_template_neq_right_val(ID, TYPE, VAL) :-
    _fch_op_neq(ID, _, A2),
    _fch_template_expr_val(A2, TYPE, VAL).

% The same identical structural references are trivially equal.
_fch_template_expr_val(ID, _fch_type_bool_id, true) :- 
    _fch_op_eq(ID, VALUE_ID, VALUE_ID).

% The same identical structural references are trivially NOT unequal.
_fch_template_expr_val(ID, _fch_type_bool_id, false) :- 
    _fch_op_neq(ID, VALUE_ID, VALUE_ID).

% The same source variables are trivially equal.
_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_eq(ID, _, _),
    _fch_same_source_binary(ID).

% The same source variables are trivially NOT unequal.
_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_neq(ID, _, _),
    _fch_same_source_binary(ID).

% =============================================================================
% SCALARS & IDS (POINTER)
% =============================================================================

% References that evaluate to the same value are equal.
_fch_template_expr_val(ID, _fch_type_bool_id, true) :- 
    _fch_op_eq(ID, A1, A2),
    not _fch_same_source_binary(ID),
    _fch_template_eq_left_val(ID, VAL_TYPE_ID, VAL),
    _fch_template_eq_right_val(ID, VAL_TYPE_ID, VAL).

% References that evaluate to the same value are NOT unequal.
_fch_template_expr_val(ID, _fch_type_bool_id, false) :- 
    _fch_op_neq(ID, A1, A2),
    not _fch_same_source_binary(ID),
    _fch_template_neq_left_val(ID, VAL_TYPE_ID, VAL),
    _fch_template_neq_right_val(ID, VAL_TYPE_ID, VAL).

% References that evaluate to different values are not equal.
_fch_template_expr_val(ID, _fch_type_bool_id, false) :- 
    _fch_op_eq(ID, A1, A2),
    not _fch_same_source_binary(ID),
    _fch_template_eq_left_val(ID, VAL_TYPE_ID, VAL_1),
    _fch_template_eq_right_val(ID, VAL_TYPE_ID, VAL_2),
    VAL_1 != VAL_2,
    VAL_TYPE_ID != _fch_type_set_id.

% References that evaluate to different values are unequal.
_fch_template_expr_val(ID, _fch_type_bool_id, true) :- 
    _fch_op_neq(ID, A1, A2),
    not _fch_same_source_binary(ID),
    _fch_template_neq_left_val(ID, VAL_TYPE_ID, VAL_1),
    _fch_template_neq_right_val(ID, VAL_TYPE_ID, VAL_2),
    VAL_1 != VAL_2,
    VAL_TYPE_ID != _fch_type_set_id.

% =============================================================================
% NONE
% =============================================================================

% None compared with a non-none value is not equal.
_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_eq(ID, A1, A2),
    not _fch_same_source_binary(ID),
    _fch_template_eq_left_val(ID, _fch_type_none_id, _),
    _fch_template_eq_right_val(ID, TYPE_2, _),
    TYPE_2 != _fch_type_none_id.

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_eq(ID, A1, A2),
    not _fch_same_source_binary(ID),
    _fch_template_eq_left_val(ID, TYPE_1, _),
    _fch_template_eq_right_val(ID, _fch_type_none_id, _),
    TYPE_1 != _fch_type_none_id.

% None compared with a non-none value is unequal.
_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_neq(ID, A1, A2),
    not _fch_same_source_binary(ID),
    _fch_template_neq_left_val(ID, _fch_type_none_id, _),
    _fch_template_neq_right_val(ID, TYPE_2, _),
    TYPE_2 != _fch_type_none_id.

_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_neq(ID, A1, A2),
    not _fch_same_source_binary(ID),
    _fch_template_neq_left_val(ID, TYPE_1, _),
    _fch_template_neq_right_val(ID, _fch_type_none_id, _),
    TYPE_1 != _fch_type_none_id.

% =============================================================================
% FLOATS & MIXED
% =============================================================================

% Equal
% @expand mixed_numeric_pairs
_fch_template_python_binary(ID, _fch_op_eq_id, (({{LEFT_TYPE}}, V1), ({{RIGHT_TYPE}}, V2))) :-
    _fch_op_eq(ID, A1, A2),
    not _fch_same_source_binary(ID),
    _fch_template_eq_left_val(ID, {{LEFT_TYPE}}, V1),
    _fch_template_eq_right_val(ID, {{RIGHT_TYPE}}, V2).
% @endexpand

% Not Equal
% @expand mixed_numeric_pairs
_fch_template_python_binary(ID, _fch_op_neq_id, (({{LEFT_TYPE}}, V1), ({{RIGHT_TYPE}}, V2))) :-
    _fch_op_neq(ID, A1, A2),
    not _fch_same_source_binary(ID),
    _fch_template_neq_left_val(ID, {{LEFT_TYPE}}, V1),
    _fch_template_neq_right_val(ID, {{RIGHT_TYPE}}, V2).
% @endexpand