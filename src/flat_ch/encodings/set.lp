% =============================================================================
% ASSIGN & BASE DOMAIN
% =============================================================================

% Every statically evaluated set assignment assigns a member to the set.
_fch_set_member_assigned(SET_NAME, TYPE, VAL) :- 
    _fch_set_assign(SET_NAME, EXPR_ID), 
    _fch_static_expr_val(EXPR_ID, TYPE, VAL).

% Every statically evaluated set base domain that is not already assigned is a candidate member of the set.
_fch_set_candidate(SET_NAME, TYPE, VAL) :-
    _fch_set_base_domain(SET_NAME, EXPR_ID), 
    _fch_static_expr_val(EXPR_ID, TYPE, VAL),
    not _fch_set_member_assigned(SET_NAME, TYPE, VAL).

% For every set, each candidate member may or may not be chosen as a dynamic member.
{ _fch_dynamic_set_member(SET_NAME, TYPE, VAL) : _fch_set_candidate(SET_NAME, TYPE, VAL) }.

% Assigned and dynamically chosen members are both real members of the set.
_fch_set_member(SET_NAME, TYPE, VAL) :- 
    _fch_set_member_assigned(SET_NAME, TYPE, VAL).

_fch_set_member(SET_NAME, TYPE, VAL) :- 
    _fch_dynamic_set_member(SET_NAME, TYPE, VAL).

% =============================================================================
% SET CONSTRUCTORS & VALUE PROPAGATION
% =============================================================================

% Create set declarations for structural set operations.
_fch_set_decl(OP_ID) :- 
    _fch_op_set_make_variadic(OP_ID, _).

_fch_set_decl(OP_ID) :- 
    _fch_op_union(OP_ID, _, _).

_fch_set_decl(OP_ID) :- 
    _fch_op_inter(OP_ID, _, _).

% `set_make` creates one set member for each nested argument expression inside our standardized variadic arg schema.
_fch_set_member(OP_ID, TYPE, VAL) :- 
    _fch_op_set_make_variadic(OP_ID, _),
    _fch_op_set_make_arg(OP_ID, _, EXPR_ID), 
    _fch_static_expr_val(EXPR_ID, TYPE, VAL).

% Static set literals should not also go through the dynamic evaluation path.
_fch_static_set_make_arg(EXPR_ID) :-
    _fch_static_expr_val(EXPR_ID, _, _).

_fch_set_member(OP_ID, TYPE, VAL) :- 
    _fch_op_set_make_variadic(OP_ID, _),
    _fch_op_set_make_arg(OP_ID, _, EXPR_ID), 
    not _fch_static_set_make_arg(EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, TYPE, VAL).

% `length` of a set evaluates to its total size.
_fch_dynamic_expr_val(OP_ID, _fch_type_int_id, SIZE) :-
    _fch_op_length(OP_ID, A1), 
    _fch_dynamic_expr_val(A1, _fch_type_set_id, SET_NAME),
    _fch_set_size(SET_NAME, SIZE).

% The set size is the total count of distinct type/value members.
_fch_set_size(SET_NAME, SIZE) :-
    _fch_set_decl(SET_NAME),
    SIZE = #count{ T, V : _fch_set_member(SET_NAME, T, V) }.

% If a variable expression tracks a structural set handle, it directly routes to that set handle.
_fch_dynamic_expr_val(EID, _fch_type_set_id, SET_NAME) :-
    _fch_expr_var(EID, SET_NAME),
    _fch_set_decl(SET_NAME).

% Operational set expressions return their own structural ID as the tracked set identifier.
_fch_dynamic_expr_val(OP_ID, _fch_type_set_id, OP_ID) :-
    _fch_op_set_make_variadic(OP_ID, _).

_fch_dynamic_expr_val(OP_ID, _fch_type_set_id, OP_ID) :-
    _fch_op_union(OP_ID, _, _).

_fch_dynamic_expr_val(OP_ID, _fch_type_set_id, OP_ID) :-
    _fch_op_inter(OP_ID, _, _).

% Bound variables evaluating to sets route their values directly through to the targeted set layout.
_fch_dynamic_expr_val(EID, _fch_type_set_id, TARGET_HANDLE) :-
    _fch_expr_var(EID, VAR_NAME),
    _fch_var_def(VAR_NAME, DEF_ID),
    _fch_dynamic_expr_val(DEF_ID, _fch_type_set_id, TARGET_HANDLE).

% =============================================================================
% SET_ISIN & SET_NOTIN
% =============================================================================

_fch_set_isin_query(OP_ID, TYPE, VAL, SET_NAME) :-
    _fch_op_set_isin(OP_ID, A1, A2), 
    _fch_dynamic_expr_val(A1, TYPE, VAL),
    _fch_dynamic_expr_val(A2, _fch_type_set_id, SET_NAME).

_fch_set_notin_query(OP_ID, TYPE, VAL, SET_NAME) :-
    _fch_op_set_notin(OP_ID, A1, A2), 
    _fch_dynamic_expr_val(A1, TYPE, VAL),
    _fch_dynamic_expr_val(A2, _fch_type_set_id, SET_NAME).

_fch_set_query_hit(OP_ID, TYPE, VAL, SET_NAME) :-
    _fch_set_isin_query(OP_ID, TYPE, VAL, SET_NAME),
    _fch_set_member(SET_NAME, TYPE, VAL).

_fch_set_query_hit(OP_ID, TYPE, VAL, SET_NAME) :-
    _fch_set_notin_query(OP_ID, TYPE, VAL, SET_NAME),
    _fch_set_member(SET_NAME, TYPE, VAL).

_fch_dynamic_expr_val(OP_ID, _fch_type_bool_id, true) :-
    _fch_set_query_hit(OP_ID, TYPE, VAL, SET_NAME),
    _fch_set_isin_query(OP_ID, TYPE, VAL, SET_NAME).

_fch_dynamic_expr_val(OP_ID, _fch_type_bool_id, false) :-
    _fch_set_isin_query(OP_ID, TYPE, VAL, SET_NAME),
    not _fch_set_query_hit(OP_ID, TYPE, VAL, SET_NAME).

_fch_dynamic_expr_val(OP_ID, _fch_type_bool_id, true) :-
    _fch_set_notin_query(OP_ID, TYPE, VAL, SET_NAME),
    not _fch_set_query_hit(OP_ID, TYPE, VAL, SET_NAME).

_fch_dynamic_expr_val(OP_ID, _fch_type_bool_id, false) :-
    _fch_set_query_hit(OP_ID, TYPE, VAL, SET_NAME),
    _fch_set_notin_query(OP_ID, TYPE, VAL, SET_NAME).

% =============================================================================
% SET EQUALITY & INEQUALITY
% =============================================================================

_fch_set_equality(OP_ID, SET_NAME_1, SET_NAME_2) :-
    _fch_op_eq(OP_ID, A1, A2), 
    _fch_dynamic_expr_val(A1, _fch_type_set_id, SET_NAME_1),
    _fch_dynamic_expr_val(A2, _fch_type_set_id, SET_NAME_2).

_fch_dynamic_expr_val(OP_ID, _fch_type_bool_id, false) :-
    _fch_set_equality(OP_ID, SET_NAME_1, SET_NAME_2),
    _fch_set_size(SET_NAME_1, N),
    _fch_set_size(SET_NAME_2, M),
    N != M.

_fch_dynamic_expr_val(OP_ID, _fch_type_bool_id, false) :-
    _fch_set_equality(OP_ID, SET_NAME_1, SET_NAME_2),
    _fch_set_member(SET_NAME_1, TYPE, VAL),
    not _fch_set_member(SET_NAME_2, TYPE, VAL).

_fch_dynamic_expr_val(OP_ID, _fch_type_bool_id, true) :-
    _fch_set_equality(OP_ID, _, _),
    not _fch_dynamic_expr_val(OP_ID, _fch_type_bool_id, false).

_fch_set_inequality(OP_ID, SET_NAME_1, SET_NAME_2) :-
    _fch_op_neq(OP_ID, A1, A2), 
    _fch_dynamic_expr_val(A1, _fch_type_set_id, SET_NAME_1),
    _fch_dynamic_expr_val(A2, _fch_type_set_id, SET_NAME_2).

_fch_dynamic_expr_val(OP_ID, _fch_type_bool_id, true) :-
    _fch_set_inequality(OP_ID, SET_NAME_1, SET_NAME_2),
    _fch_set_size(SET_NAME_1, N),
    _fch_set_size(SET_NAME_2, M),
    N != M.

_fch_dynamic_expr_val(OP_ID, _fch_type_bool_id, true) :-
    _fch_set_inequality(OP_ID, SET_NAME_1, SET_NAME_2),
    _fch_set_member(SET_NAME_1, TYPE, VAL),
    not _fch_set_member(SET_NAME_2, TYPE, VAL).

_fch_dynamic_expr_val(OP_ID, _fch_type_bool_id, false) :-
    _fch_set_inequality(OP_ID, _, _),
    not _fch_dynamic_expr_val(OP_ID, _fch_type_bool_id, true).

% =============================================================================
% UNION & INTERSECTION
% =============================================================================

_fch_set_member(OP_ID, TYPE, VAL) :- 
    _fch_op_union(OP_ID, A1, _), 
    _fch_set_decl(OP_ID),
    _fch_dynamic_expr_val(A1, _fch_type_set_id, SET_NAME_1),
    _fch_set_member(SET_NAME_1, TYPE, VAL).

_fch_set_member(OP_ID, TYPE, VAL) :- 
    _fch_op_union(OP_ID, _, A2), 
    _fch_set_decl(OP_ID),
    _fch_dynamic_expr_val(A2, _fch_type_set_id, SET_NAME_2),
    _fch_set_member(SET_NAME_2, TYPE, VAL).

_fch_set_member(OP_ID, TYPE, VAL) :-
    _fch_op_inter(OP_ID, A1, A2), 
    _fch_set_decl(OP_ID),
    _fch_dynamic_expr_val(A1, _fch_type_set_id, SET_NAME_1),
    _fch_dynamic_expr_val(A2, _fch_type_set_id, SET_NAME_2),
    _fch_set_member(SET_NAME_1, TYPE, VAL),
    _fch_set_member(SET_NAME_2, TYPE, VAL).

% =============================================================================
% SUBSET
% =============================================================================

_fch_set_subset(OP_ID, SET_NAME_1, SET_NAME_2) :-
    _fch_op_subset(OP_ID, A1, A2), 
    _fch_dynamic_expr_val(A1, _fch_type_set_id, SET_NAME_1),
    _fch_dynamic_expr_val(A2, _fch_type_set_id, SET_NAME_2).

_fch_dynamic_expr_val(OP_ID, _fch_type_bool_id, false) :-
    _fch_set_subset(OP_ID, SET_NAME_1, SET_NAME_2),
    _fch_set_size(SET_NAME_1, N),
    _fch_set_size(SET_NAME_2, M),
    N > M.

_fch_dynamic_expr_val(OP_ID, _fch_type_bool_id, false) :-
    _fch_set_subset(OP_ID, SET_NAME_1, SET_NAME_2),
    _fch_set_member(SET_NAME_1, TYPE, VAL),
    not _fch_set_member(SET_NAME_2, TYPE, VAL).

_fch_dynamic_expr_val(OP_ID, _fch_type_bool_id, true) :-
    _fch_set_subset(OP_ID, _, _),
    not _fch_dynamic_expr_val(OP_ID, _fch_type_bool_id, false).

% =============================================================================
% DYNAMIC RUNTIME PYTHON OUTPUT SET UNPACKING
% =============================================================================

_fch_set_from_python(ID, MEMBERS) :-  
    _fch_python_exec_val(ID, _fch_type_set_id, MEMBERS).

_fch_dynamic_expr_val(ID, _fch_type_set_id, ID) :- 
    _fch_python_exec_val(ID, _fch_type_set_id, _).

_fch_set_decl(ID) :- 
    _fch_set_from_python(ID, _).

_fch_set_member_unpacking(ID, MEMBER, TAIL) :- 
    _fch_set_from_python(ID, (MEMBER, TAIL)).

_fch_set_member_unpacking(ID, MEMBER, TAIL) :- 
    _fch_set_member_unpacking(ID, _, (MEMBER, TAIL)), 
    TAIL != ().

% Mapping dynamic target wrapper variables seamlessly back to constants
_fch_set_member(ID, _fch_type_none_id, VALUE) :- _fch_set_member_unpacking(ID, val(none, VALUE), _).
_fch_set_member(ID, _fch_type_int_id, VALUE) :- _fch_set_member_unpacking(ID, val(int, VALUE), _).
_fch_set_member(ID, _fch_type_float_id, VALUE) :- _fch_set_member_unpacking(ID, val(float, VALUE), _).
_fch_set_member(ID, _fch_type_string_id, VALUE) :- _fch_set_member_unpacking(ID, val(string, VALUE), _).
_fch_set_member(ID, _fch_type_bool_id, VALUE) :- _fch_set_member_unpacking(ID, val(bool, VALUE), _).