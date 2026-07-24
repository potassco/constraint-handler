% =============================================================================
% ALIASING
% =============================================================================

% A variable is a pure alias only when its domain has one expression.
_fch_var_singleton_domain(NAME) :-
    _fch_var_dom(NAME, _),
    1 = #count { EXPR_ID : _fch_var_dom(NAME, EXPR_ID) }.

_fch_var_direct_alias(NAME, TARGET_NAME) :-
    _fch_var_dom(NAME, EXPR_ID),
    _fch_expr_var(EXPR_ID, TARGET_NAME),
    NAME != TARGET_NAME,
    _fch_var_singleton_domain(NAME).

% A variable definition that only forwards another variable is also a pure alias.
_fch_var_direct_alias(NAME, TARGET_NAME) :-
    _fch_var_def(NAME, EXPR_ID),
    _fch_expr_var(EXPR_ID, TARGET_NAME),
    NAME != TARGET_NAME.

_fch_var_alias_parent(NAME) :-
    _fch_var_direct_alias(NAME, _).

_fch_var_root(NAME, NAME) :-
    _fch_expr_var(_, NAME),
    not _fch_var_alias_parent(NAME).

_fch_var_root(NAME, ROOT_NAME) :-
    _fch_var_direct_alias(NAME, TARGET_NAME),
    _fch_var_root(TARGET_NAME, ROOT_NAME).

_fch_comparison(ID, LEFT_ID, RIGHT_ID) :-
    _fch_op_eq(ID, LEFT_ID, RIGHT_ID).

_fch_comparison(ID, LEFT_ID, RIGHT_ID) :-
    _fch_op_neq(ID, LEFT_ID, RIGHT_ID).

_fch_same_source_binary(ID) :-
    _fch_comparison(ID, LEFT_ID, RIGHT_ID),
    _fch_expr_var(LEFT_ID, LEFT_NAME),
    _fch_expr_var(RIGHT_ID, RIGHT_NAME),
    _fch_var_root(LEFT_NAME, ROOT_NAME),
    _fch_var_root(RIGHT_NAME, ROOT_NAME).
