% =============================================================================
% HASVALUE
% =============================================================================

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_hasValue(ID, A1),
    _fch_template_expr_val(A1, _fch_type_none_id, none).

_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_hasValue(ID, A1),
    _fch_template_expr_val(A1, VALUE_TYPE, _),
    VALUE_TYPE != _fch_type_none_id.

% =============================================================================
% IF
% =============================================================================

_fch_template_if_true(ID, THEN_ID) :-
    _fch_op_if(ID, CONDITION_ID, THEN_ID),
    _fch_template_expr_val(CONDITION_ID, _fch_type_bool_id, true).

_fch_template_expr_val(ID, THEN_TYPE, THEN_VALUE) :-
    _fch_template_if_true(ID, THEN_ID),
    _fch_template_expr_val(THEN_ID, THEN_TYPE, THEN_VALUE).

_fch_template_expr_val(ID, _fch_type_none_id, none) :-
    _fch_op_if(ID, CONDITION_ID, _),
    _fch_template_expr_val(CONDITION_ID, _fch_type_bool_id, false).

_fch_template_expr_val(ID, _fch_type_none_id, none) :-
    _fch_op_if(ID, CONDITION_ID, _),
    _fch_template_expr_val(CONDITION_ID, _fch_type_none_id, none).

% =============================================================================
% ITE (Ternary Shape)
% =============================================================================

_fch_template_ite_then_val(ID, TYPE, VALUE) :-
    _fch_op_ite(ID, _, THEN_ID, _),
    _fch_template_expr_val(THEN_ID, TYPE, VALUE).

_fch_template_ite_else_val(ID, TYPE, VALUE) :-
    _fch_op_ite(ID, _, _, ELSE_ID),
    _fch_template_expr_val(ELSE_ID, TYPE, VALUE).

_fch_template_ite_cond(ID, true) :-
    _fch_op_ite(ID, CONDITION_ID, _, _),
    _fch_template_expr_val(CONDITION_ID, _fch_type_bool_id, true).

_fch_template_ite_cond(ID, false) :-
    _fch_op_ite(ID, CONDITION_ID, _, _),
    _fch_template_expr_val(CONDITION_ID, _fch_type_bool_id, false).

_fch_template_expr_val(ID, THEN_TYPE, THEN_VALUE) :-
    _fch_template_ite_cond(ID, true),
    _fch_template_ite_then_val(ID, THEN_TYPE, THEN_VALUE).

_fch_template_expr_val(ID, ELSE_TYPE, ELSE_VALUE) :-
    _fch_template_ite_cond(ID, false),
    _fch_template_ite_else_val(ID, ELSE_TYPE, ELSE_VALUE).

_fch_template_expr_val(ID, _fch_type_none_id, none) :-
    _fch_op_ite(ID, CONDITION_ID, _, _),
    _fch_template_expr_val(CONDITION_ID, _fch_type_none_id, none).

% =============================================================================
% LIMP
% =============================================================================

% If the first argument is `false`, the result is always `true`.
_fch_template_expr_val(ID, _fch_type_bool_id, true) :- 
    _fch_op_limp(ID, A1, _),
    _fch_template_expr_val(A1, _fch_type_bool_id, false).

% If the second argument is `true`, the result is always `true`.
_fch_template_expr_val(ID, _fch_type_bool_id, true) :- 
    _fch_op_limp(ID, _, A2),
    _fch_template_expr_val(A2, _fch_type_bool_id, true).

_fch_template_has_true(ID)  :- _fch_template_expr_val(ID, _, true).
_fch_template_has_false(ID) :- _fch_template_expr_val(ID, _, false).

% This projection was added because I use Clingo 6 for profiling and
% Clingo 6 actually explodes here without this projection.
_fch_template_limp_left_true(ID, A2) :-
    _fch_op_limp(ID, A1, A2),
    _fch_template_expr_val(A1, _fch_type_bool_id, true).

_fch_template_expr_val(ID, _fch_type_bool_id, false) :- 
    _fch_template_limp_left_true(ID, A2),
    _fch_template_expr_val(A2, _fch_type_bool_id, false).

_fch_template_expr_val(ID, _fch_type_none_id, none) :-
    _fch_op_limp(ID, _, _),
    not _fch_template_has_true(ID),
    not _fch_template_has_false(ID).

% =============================================================================
% LNOT
% =============================================================================

_fch_template_expr_val(ID, _fch_type_bool_id, true) :-
    _fch_op_lnot(ID, A1),
    _fch_template_expr_val(A1, _fch_type_bool_id, false).

_fch_template_expr_val(ID, _fch_type_bool_id, false) :-
    _fch_op_lnot(ID, A1),
    _fch_template_expr_val(A1, _fch_type_bool_id, true).

_fch_template_expr_val(ID, _fch_type_none_id, none) :-
    _fch_op_lnot(ID, A1),
    _fch_template_expr_val(A1, _fch_type_none_id, none).

% =============================================================================
% DISJ
% =============================================================================

_fch_template_expr_val(ID, _fch_type_bool_id, true) :- 
    _fch_op_disj_variadic(ID, _),
    _fch_op_disj_arg(ID, _, A),
    _fch_template_expr_val(A, _fch_type_bool_id, true).

_fch_template_expr_val(ID, _fch_type_bool_id, false) :- 
    _fch_op_disj_variadic(ID, _),
    #false : _fch_op_disj_arg(ID, _, A), not _fch_template_expr_val(A, _fch_type_bool_id, false).

_fch_template_expr_val(ID, _fch_type_none_id, none) :-
    _fch_op_disj_variadic(ID, _),
    _fch_op_disj_arg(ID, _, A),
    _fch_template_expr_val(A, _fch_type_none_id, none),
    not _fch_template_has_true(ID),
    not _fch_template_has_false(ID).

% =============================================================================
% CONJ
% =============================================================================

_fch_template_expr_val(ID, _fch_type_bool_id, false) :- 
    _fch_op_conj_variadic(ID, _),
    _fch_op_conj_arg(ID, _, A),
    _fch_template_expr_val(A, _fch_type_bool_id, false).

_fch_template_expr_val(ID, _fch_type_bool_id, true) :- 
    _fch_op_conj_variadic(ID, _),
    #false : _fch_op_conj_arg(ID, _, A), not _fch_template_expr_val(A, _fch_type_bool_id, true).

_fch_template_expr_val(ID, _fch_type_none_id, none) :-
    _fch_op_conj_variadic(ID, _),
    _fch_op_conj_arg(ID, _, A),
    _fch_template_expr_val(A, _fch_type_none_id, none),
    not _fch_template_has_true(ID),
    not _fch_template_has_false(ID).