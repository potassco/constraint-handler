% =============================================================================
% DICT CONSTRUCTORS
% =============================================================================

_fch_dict(OP_ID) :- 
    _fch_op_dict_make_variadic(OP_ID, _).

_fch_dict_entry(OP_ID, KEY_ID, VALUE_ID) :- 
    _fch_op_dict_make_variadic(OP_ID, _),
    _fch_op_dict_make_arg(OP_ID, _, PAIR_ID), 
    _fch_pair(PAIR_ID, KEY_ID, VALUE_ID).

% =============================================================================
% DICT SELECTION
% =============================================================================

_fch_dict_selection_resolved(OP_ID, DICT_ID, KEY_ID) :-
    _fch_op_dict_select(OP_ID, A1, A2),
    _fch_dynamic_expr_val(A1, _, KEY_ID),
    _fch_dynamic_expr_val(A2, _, DICT_ID),
    _fch_dict(DICT_ID).

_fch_dynamic_expr_val(OP_ID, TYPE, VALUE) :- 
    _fch_dict_selection_resolved(OP_ID, DICT_ID, KEY_ID),
    _fch_dict_entry(DICT_ID, KEY_ID, VALUE_ID),
    _fch_dynamic_expr_val(VALUE_ID, TYPE, VALUE).