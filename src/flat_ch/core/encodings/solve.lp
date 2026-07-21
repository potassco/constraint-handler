% =============================================================================
% STATIC
% =============================================================================

% All values coming out of the flattening process are already evaluated.
% Right now, these are only constant values.
_fch_static_expr_val(ID, TYPE, VAL) :-
    _fch_expr_val(ID, TYPE, VAL).

% The value of a defined variable is the value of its defining expression.
_fch_static_expr_val(ID, TYPE, VAL) :-
    _fch_expr_var(ID, NAME),
    _fch_var_def(NAME, EXPR_ID),
    _fch_static_expr_val(EXPR_ID, TYPE, VAL).

% The value of an expression that can be evaluated by Python is the result of that evaluation.
_fch_static_expr_val(ID, TYPE_ID, VALUE) :-
    _fch_static_python_binary(ID, OPERATOR_ID, ARGS),
    (TYPE_ID, VALUE) = @fch_operation(OPERATOR_ID, ARGS).

_fch_static_expr_val(ID, TYPE_ID, VALUE) :-
    _fch_static_python_unary(ID, OPERATOR_ID, ARGS),
    (TYPE_ID, VALUE) = @fch_operation(OPERATOR_ID, ARGS).


% =============================================================================
% DYNAMIC
% =============================================================================

% All static values are considered to be already resolved in the dynamic evaluation as well.
_fch_dynamic_expr_val(ID, TYPE, VAL) :-
    _fch_static_expr_val(ID, TYPE, VAL).

% For each declared variable we pick exactly one expression from its domain to define it.
% This must also happen for variables that are only observed via public output.
1{_fch_dynamic_var_def(NAME, EXPR_ID) : _fch_var_dom(NAME, EXPR_ID)}1 :-
    _fch_var_decl(NAME),
    _fch_var_dom(NAME, _).

_fch_dynamic_var_def_val(NAME, EXPR_ID, TYPE, VAL) :-
    _fch_dynamic_var_def(NAME, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, TYPE, VAL).

% A chosen domain entry must resolve to an actual value.
:- _fch_dynamic_var_def(NAME, EXPR_ID),
    not _fch_dynamic_expr_val(EXPR_ID, _, _).

_fch_dynamic_dom_val(NAME, DOM_EXPR_ID, TYPE, VAL) :-
    _fch_var_dom(NAME, DOM_EXPR_ID),
    _fch_dynamic_expr_val(DOM_EXPR_ID, TYPE, VAL).

% Equivalent domain expressions should not create duplicate models.
% Replaces the unindexed global join to prevent millions of evaluation match checks.
:- _fch_dynamic_var_def_val(NAME, EXPR_ID, TYPE, VAL),
    _fch_dynamic_dom_val(NAME, EARLIER_EXPR_ID, TYPE, VAL),
    EARLIER_EXPR_ID < EXPR_ID.

% The value of a declared variable is the value of the expression that we have chosen to define it.
_fch_dynamic_expr_val(ID, TYPE, VAL) :-
    _fch_expr_var(ID, NAME),
    _fch_dynamic_var_def(NAME, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, TYPE, VAL).

% The value of a defined variable is the dynamic value of its defining expression.
_fch_dynamic_expr_val(ID, TYPE, VAL) :-
    _fch_expr_var(ID, NAME),
    _fch_var_def(NAME, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, TYPE, VAL).

% In CH, execution outputs of declared but inactive executions resolve to none.
_fch_inactive_execution_output((EXEC, VAR, out)) :-
    _fch_flat(execution_output_decl(EXEC, VAR)),
    not _fch_execution_run(EXEC).

% Declared variables without any domain entries are treated as invalid inputs.
_fch_empty_var_domain(NAME) :-
    _fch_var_decl(NAME),
    not _fch_var_dom(NAME, _).

:- _fch_empty_var_domain(NAME),
    not _fch_inactive_execution_output(NAME).

_fch_dynamic_expr_val(ID, _fch_type_none_id, none) :-
    _fch_expr_var(ID, NAME),
    _fch_inactive_execution_output(NAME).

_fch_dynamic_expr_val(ID, _fch_type_fail_id, empty_domain(NAME)) :-
    _fch_expr_var(ID, NAME),
    _fch_empty_var_domain(NAME),
    not _fch_inactive_execution_output(NAME).

% Referencing a variable that has neither a declaration nor a definition is a failure.
_fch_dynamic_expr_val(ID, _fch_type_fail_id, undefined_variable(NAME)) :-
    _fch_expr_var(ID, NAME),
    not _fch_var_decl(NAME),
    not _fch_var_def(NAME, _),
    not _fch_set_decl(NAME),
	not _fch_inactive_execution_output(NAME).

% Failures on strict child expressions propagate to the parent expression.
_fch_dynamic_expr_val(ID, _fch_type_fail_id, VALUE) :-
    _fch_op_strict_child(ID, CHILD_ID),
    _fch_dynamic_expr_val(CHILD_ID, _fch_type_fail_id, VALUE).

% Only failures on expressions that are needed for feasibility or optimization
% should invalidate the model. This prevents failed python executions from failing
% the model even though it wasn't needed anyways.
_fch_dynamic_expr_needed(EXPR_ID) :-
    _fch_ensure(_, EXPR_ID).

_fch_dynamic_expr_needed(EXPR_ID) :-
    _fch_optimize_sum(EXPR_ID, _, _).

_fch_dynamic_expr_needed(CHILD_ID) :-
    _fch_dynamic_expr_needed(PARENT_ID),
    _fch_op_strict_child(PARENT_ID, CHILD_ID).

_fch_dynamic_expr_needed(KEY_ID) :-
    _fch_dynamic_expr_needed(PAIR_ID),
    _fch_pair(PAIR_ID, KEY_ID, _).

_fch_dynamic_expr_needed(VALUE_ID) :-
    _fch_dynamic_expr_needed(PAIR_ID),
    _fch_pair(PAIR_ID, _, VALUE_ID).

_fch_dynamic_expr_needed(EXPR_ID) :-
    _fch_dynamic_expr_needed(ID),
    _fch_expr_var(ID, NAME),
    _fch_dynamic_var_def(NAME, EXPR_ID).

_fch_dynamic_expr_needed(EXPR_ID) :-
    _fch_dynamic_expr_needed(ID),
    _fch_expr_var(ID, NAME),
    _fch_var_def(NAME, EXPR_ID).

_fch_dynamic_expr_needed(CONDITION_ID) :-
    _fch_dynamic_expr_needed(ID),
    _fch_op_if(ID, CONDITION_ID, _).

_fch_dynamic_expr_needed(THEN_ID) :-
    _fch_dynamic_expr_needed(ID),
    _fch_op_if(ID, CONDITION_ID, THEN_ID),
    _fch_dynamic_expr_val(CONDITION_ID, _fch_type_bool_id, true).

_fch_dynamic_expr_needed(CONDITION_ID) :-
    _fch_dynamic_expr_needed(ID),
    _fch_op_ite(ID, CONDITION_ID, _, _).

_fch_dynamic_expr_needed(THEN_ID) :-
    _fch_dynamic_expr_needed(ID),
    _fch_op_ite(ID, CONDITION_ID, THEN_ID, _),
    _fch_dynamic_expr_val(CONDITION_ID, _fch_type_bool_id, true).

_fch_dynamic_expr_needed(ELSE_ID) :-
    _fch_dynamic_expr_needed(ID),
    _fch_op_ite(ID, CONDITION_ID, _, ELSE_ID),
    _fch_dynamic_expr_val(CONDITION_ID, _fch_type_bool_id, false).

% All ensures must be satisfied for the solution to be valid.
:- _fch_ensure(NAME, EXPR_ID),
    not _fch_dynamic_expr_val(EXPR_ID, _fch_type_bool_id, true).

% The value of an expression that can be evaluated by Python is the result of that evaluation.
_fch_dynamic_expr_val(ID, TYPE_ID, VALUE) :-
    _fch_dynamic_python_binary(ID, OPERATOR_ID, ARGS),
    (TYPE_ID, VALUE) = @fch_operation(OPERATOR_ID, ARGS).

_fch_dynamic_expr_val(ID, TYPE_ID, VALUE) :-
    _fch_dynamic_python_unary(ID, OPERATOR_ID, ARGS),
    (TYPE_ID, VALUE) = @fch_operation(OPERATOR_ID, ARGS).


% It cannot be the case that some integrity fail was thrown from python.
:- _fch_dynamic_expr_needed(ID),
    _fch_dynamic_expr_val(ID, _fch_type_fail_id, _).

% Undefined references are always fatal, even if they only occur on a branch
% that would otherwise be skippable.
:- _fch_dynamic_expr_val(_, _fch_type_fail_id, undefined_variable(_)).

% =============================================================================
% OPTIMIZATION OBJECTIVES
% =============================================================================

_fch_optimize_priority(Level) :-
    _fch_optimize_sum(_, _, Level).

_fch_optimize_precision_value(Level, Precision) :-
    _fch_optimize_precision(ExprId, Level),
    _fch_dynamic_expr_val(ExprId, _fch_type_int_id, Precision).

_fch_optimize_precision_value(Level, Precision) :-
    _fch_optimize_priority(Level),
    _fch_optimize_precision(ExprId, all),
    _fch_dynamic_expr_val(ExprId, _fch_type_int_id, Precision),
    not _fch_optimize_precision(_, Level).

_fch_optimize_precision_value(Level, 1) :-
    _fch_optimize_priority(Level),
    not _fch_optimize_precision(_, Level),
    not _fch_optimize_precision(_, all).

_fch_optimize_weight_by_expr(ExprId, Level, Value) :-
    _fch_optimize_sum(ExprId, Key, Level),
    _fch_optimize_precision_value(Level, Precision),
    _fch_dynamic_expr_val(ExprId, _fch_type_int_id, BaseValue),
    Value = BaseValue * Precision.

_fch_optimize_weight_by_expr(ExprId, Level, Value) :-
    _fch_optimize_sum(ExprId, Key, Level),
    _fch_optimize_precision_value(Level, Precision),
    _fch_dynamic_expr_val(ExprId, _fch_type_bool_id, true),
    Value = Precision.

_fch_optimize_weight_by_expr(ExprId, Level, 0) :-
    _fch_optimize_sum(ExprId, Key, Level),
    _fch_dynamic_expr_val(ExprId, _fch_type_bool_id, false).

_fch_optimize_weight_by_expr(ExprId, Level, IntValue) :-
    _fch_optimize_sum(ExprId, Key, Level),
    _fch_optimize_precision_value(Level, Precision),
    _fch_dynamic_expr_val(ExprId, _fch_type_float_id, FloatValue),
    IntValue = @fch_scaled_float_to_int(FloatValue, Precision).

_fch_optimize_weight(Key, Level, Value) :-
	_fch_optimize_sum(ExprId, Key, Level),
	_fch_optimize_weight_by_expr(ExprId, Level, Value).

#maximize { Value@Level, Key : _fch_optimize_weight(Key, Level, Value) }.
