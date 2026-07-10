% =============================================================================
% ALIASING
% =============================================================================

% A declared variable with more than one domain expression is not a pure alias.
_fch_var_dom_extra(NAME, EXPR_ID) :-
    _fch_var_dom(NAME, EXPR_ID),
    _fch_var_dom(NAME, OTHER_EXPR_ID),
    OTHER_EXPR_ID != EXPR_ID.

% A singleton variable domain that forwards directly to another variable is a pure alias.
_fch_var_direct_alias(NAME, TARGET_NAME) :-
    _fch_var_dom(NAME, EXPR_ID),
    _fch_expr_var(EXPR_ID, TARGET_NAME),
    NAME != TARGET_NAME,
    not _fch_var_dom_extra(NAME, EXPR_ID).

% A variable definition that only forwards another variable is also a pure alias.
_fch_var_direct_alias(NAME, TARGET_NAME) :-
    _fch_var_def(NAME, EXPR_ID),
    _fch_expr_var(EXPR_ID, TARGET_NAME),
    NAME != TARGET_NAME.

_fch_var_alias_parent(NAME) :-
    _fch_var_direct_alias(NAME, _).

% Canonical root for variables that are not pure aliases.
_fch_var_root(NAME, NAME) :-
    _fch_expr_var(_, NAME),
    not _fch_var_alias_parent(NAME).

% Canonical root for variables that forward into another variable.
_fch_var_root(NAME, ROOT_NAME) :-
    _fch_var_direct_alias(NAME, TARGET_NAME),
    _fch_var_root(TARGET_NAME, ROOT_NAME).

% Two expression ids definitely refer to the same underlying source variable.
_fch_same_source_expr(LEFT_ID, RIGHT_ID) :-
    _fch_expr_var(LEFT_ID, LEFT_NAME),
    _fch_expr_var(RIGHT_ID, RIGHT_NAME),
    _fch_var_root(LEFT_NAME, ROOT_NAME),
    _fch_var_root(RIGHT_NAME, ROOT_NAME).

% Binary operation where both operands refer to the same underlying source variable.
_fch_same_source_binary(ID) :-
    _fch_op_eq(ID, LEFT_ID, RIGHT_ID),
    _fch_same_source_expr(LEFT_ID, RIGHT_ID).

_fch_same_source_binary(ID) :-
    _fch_op_neq(ID, LEFT_ID, RIGHT_ID),
    _fch_same_source_expr(LEFT_ID, RIGHT_ID).