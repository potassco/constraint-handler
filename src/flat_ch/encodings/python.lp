% =============================================================================
% PYTHON EXECUTION
% =============================================================================

_fch_python_set_member_typed(SET_ID, (TYPE, VALUE)) :-
    _fch_python_serialized_set(SET_ID),
    _fch_set_member(SET_ID, TYPE, VALUE).

_fch_python_serialized_set(SET_ID) :-
    _fch_op_python_arg(ID, _, EXPR_ID),
    not _fch_expr_var(ID, _),
    _fch_dynamic_expr_val(EXPR_ID, _fch_type_set_id, SET_ID).

_fch_python_set_serialized(SET_ID, INDEX, ()) :-
    _fch_set_size(SET_ID, SIZE),
    INDEX = SIZE + 1.

_fch_python_set_serialized(SET_ID, INDEX, (TYPED_VALUE, TAIL)) :-
    _fch_python_set_member_typed(SET_ID, TYPED_VALUE),
    COUNT = #count { OTHER : _fch_python_set_member_typed(SET_ID, OTHER), OTHER < TYPED_VALUE },
    INDEX = COUNT + 1,
    NEXT = INDEX + 1,
    _fch_python_set_serialized(SET_ID, NEXT, TAIL).

% Base Case: Anchor the execution tree directly to the python operator variant.
python_arg_prepared(ID, 0, ()) :-
    _fch_op_python_variadic(ID, _).

% Inductive Case: Collect variables sequentially using our uniform variadic arg schema.
python_arg_prepared(ID, INDEX, ((EXPR_ID, (TYPE, VALUE)), TAIL)) :-
    python_arg_prepared(ID, INDEX - 1, TAIL),
    _fch_op_python_variadic(ID, LEN),
    _fch_op_python_arg(ID, INDEX, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, TYPE, VALUE),
    TYPE != _fch_type_set_id,
    INDEX <= LEN.

python_arg_prepared(ID, INDEX, ((EXPR_ID, (_fch_type_set_id, MEMBERS)), TAIL)) :-
    python_arg_prepared(ID, INDEX - 1, TAIL),
    _fch_op_python_variadic(ID, LEN),
    _fch_op_python_arg(ID, INDEX, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, _fch_type_set_id, SET_ID),
    _fch_python_set_serialized(SET_ID, 1, MEMBERS),
    INDEX <= LEN.

% Trigger the execution loop once all sequential slots have packed their values.
_fch_python_execution_ready(ID, ARGS) :-
    python_arg_prepared(ID, LEN, ARGS),
    _fch_op_python_variadic(ID, LEN),
    not _fch_python_has_failed_arg(ID).

% Python operators already inherit child failures through strict-child propagation.
% Avoid calling into the Python bridge when any prepared argument is a fail value.
_fch_python_has_failed_arg(ID) :-
    _fch_op_python_arg(ID, _, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, _fch_type_fail_id, _).

% Fire the external python registry FFI engine.
_fch_python_exec_val(ID, TYPE_ID, VALUE) :-
    _fch_python_execution_ready(ID, ARGS),
    (TYPE_ID, VALUE) = @fch_py_operation(ID, ARGS).

% Stream the executed payload right back into the main evaluation loop.
_fch_dynamic_expr_val(ID, TYPE_ID, VALUE) :-
    _fch_python_exec_val(ID, TYPE_ID, VALUE),
    TYPE_ID != _fch_type_set_id.
