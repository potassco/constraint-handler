% =============================================================================
% PYTHON EXECUTION
% =============================================================================

% Base Case: Anchor the execution tree directly to the python operator variant.
python_arg_prepared(ID, 0, ()) :- 
    _fch_op_python_variadic(ID, _).

% Inductive Case: Collect variables sequentially using our uniform variadic arg schema.
python_arg_prepared(ID, INDEX, ((EXPR_ID, (TYPE, VALUE)), TAIL)) :- 
    python_arg_prepared(ID, INDEX - 1, TAIL),
    _fch_op_python_variadic(ID, LEN),
    _fch_op_python_arg(ID, INDEX, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, TYPE, VALUE),
    INDEX <= LEN.

% Trigger the execution loop once all sequential slots have packed their values.
_fch_python_execution_ready(ID, ARGS) :- 
    python_arg_prepared(ID, LEN, ARGS),
    _fch_op_python_variadic(ID, LEN).

% Fire the external python registry FFI engine.
_fch_python_exec_val(ID, TYPE_ID, VALUE) :- 
    _fch_python_execution_ready(ID, ARGS),
    (TYPE_ID, VALUE) = @fch_py_operation(ID, ARGS).

% Stream the executed payload right back into the main evaluation loop.
_fch_dynamic_expr_val(ID, TYPE_ID, VALUE) :- 
    _fch_python_exec_val(ID, TYPE_ID, VALUE), 
    TYPE_ID != _fch_type_set_id.