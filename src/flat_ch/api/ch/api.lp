%
% Additional CH-facing API declarations.
% This file only forwards legacy CH arities that are not already covered by encodings/api.lp.
%

#defined variable_declare/2.
#defined variable_declare/3.
_fch_input(variable_declare(_fch_label, NAME, DOMAIN)) :- variable_declare(NAME, DOMAIN).
_fch_input(variable_declare(LABEL, NAME, DOMAIN)) :- variable_declare(LABEL, NAME, DOMAIN).

#defined variable_define/2.
#defined variable_define/3.
_fch_input(variable_define(_fch_label, NAME, EXPR)) :- variable_define(NAME, EXPR).
_fch_input(variable_define(LABEL, NAME, EXPR)) :- variable_define(LABEL, NAME, EXPR).

#defined variable_domain/2.
#defined variable_domain/3.
_fch_input(variable_domain(_fch_label, NAME, EXPR)) :- variable_domain(NAME, EXPR).
_fch_input(variable_domain(LABEL, NAME, EXPR)) :- variable_domain(LABEL, NAME, EXPR).

% variable_choice is a domain-population alias, just like in CH's own compile2/propagator engines.
#defined variable_choice/2.
#defined variable_choice/3.
_fch_input(variable_domain(_fch_label, NAME, EXPR)) :- variable_choice(NAME, EXPR).
_fch_input(variable_domain(LABEL, NAME, EXPR)) :- variable_choice(LABEL, NAME, EXPR).

% variable_assign forces a value, exactly like variable_define.
#defined variable_assign/2.
#defined variable_assign/3.
_fch_input(variable_define(_fch_label, NAME, EXPR)) :- variable_assign(NAME, EXPR).
_fch_input(variable_define(LABEL, NAME, EXPR)) :- variable_assign(LABEL, NAME, EXPR).

#defined variable_default/2.
#defined variable_default/3.
#defined variable_default/4.
#defined variable_default/5.
_fch_input(variable_default(_fch_label, NAME, DEFAULT, val(bool, true), 0)) :- variable_default(NAME, DEFAULT).
_fch_input(variable_default(_fch_label, NAME, DEFAULT, CONDITION, 0)) :- variable_default(NAME, DEFAULT, CONDITION).
_fch_input(variable_default(_fch_label, NAME, DEFAULT, CONDITION, PRIORITY)) :- variable_default(NAME, DEFAULT, CONDITION, PRIORITY).
_fch_input(variable_default(LABEL, NAME, DEFAULT, CONDITION, PRIORITY)) :- variable_default(LABEL, NAME, DEFAULT, CONDITION, PRIORITY).

#defined ensure/1.
#defined ensure/2.
_fch_input(ensure(__anonymous, EXPR)) :- ensure(EXPR).
_fch_input(ensure(LABEL, EXPR)) :- ensure(LABEL, EXPR).

#defined evaluate/1.
#defined evaluate/2.
_fch_input(evaluate(_fch_label, EXPR)) :- evaluate(EXPR).
_fch_input(evaluate(LABEL, EXPR)) :- evaluate(LABEL, EXPR).

#defined bool_evaluate/1.
#defined bool_evaluate/2.
_fch_input(bool_evaluate(_fch_label, EXPR)) :- bool_evaluate(EXPR).
_fch_input(bool_evaluate(LABEL, EXPR)) :- bool_evaluate(LABEL, EXPR).

#defined set_declare/1.
#defined set_declare/2.
_fch_input(set_declare(_fch_label, NAME)) :- set_declare(NAME).
_fch_input(set_declare(LABEL, NAME)) :- set_declare(LABEL, NAME).

#defined set_baseDomain/2.
#defined set_baseDomain/3.
_fch_input(set_baseDomain(_fch_label, NAME, EXPR)) :- set_baseDomain(NAME, EXPR).
_fch_input(set_baseDomain(LABEL, NAME, EXPR)) :- set_baseDomain(LABEL, NAME, EXPR).

#defined set_assign/2.
#defined set_assign/3.
_fch_input(set_assign(_fch_label, NAME, EXPR)) :- set_assign(NAME, EXPR).
_fch_input(set_assign(LABEL, NAME, EXPR)) :- set_assign(LABEL, NAME, EXPR).

#defined optimize_maximizeSum/2.
#defined optimize_maximizeSum/3.
#defined optimize_maximizeSum/4.
_fch_input(optimize_maximizeSum(_fch_label, EXPR, ELEMENT, 0)) :- optimize_maximizeSum(EXPR, ELEMENT).
_fch_input(optimize_maximizeSum(_fch_label, EXPR, ELEMENT, PRIORITY)) :- optimize_maximizeSum(EXPR, ELEMENT, PRIORITY).
_fch_input(optimize_maximizeSum(LABEL, EXPR, ELEMENT, PRIORITY)) :- optimize_maximizeSum(LABEL, EXPR, ELEMENT, PRIORITY).

#defined optimize_precision/1.
#defined optimize_precision/2.
_fch_input(optimize_precision(EXPR, PRIORITY)) :- optimize_precision(EXPR, PRIORITY).
_fch_input(optimize_precision(EXPR, all)) :- optimize_precision(EXPR).

#defined execution_declare/4.
#defined execution_declare/5.
_fch_input(execution_declare(_fch_label, NAME, STATEMENTS, INPUT, OUTPUT)) :- execution_declare(NAME, STATEMENTS, INPUT, OUTPUT).
_fch_input(execution_declare(LABEL, NAME, STATEMENTS, INPUT, OUTPUT)) :- execution_declare(LABEL, NAME, STATEMENTS, INPUT, OUTPUT).

_fch_execution_decl_meta(execution_declare(LABEL, NAME, STATEMENTS, INPUT, OUTPUT)) :- execution_declare(LABEL, NAME, STATEMENTS, INPUT, OUTPUT).

#defined execution_run/1.
#defined execution_run/2.
_fch_input(execution_run(_fch_label, NAME)) :- execution_run(NAME).
_fch_input(execution_run(LABEL, NAME)) :- execution_run(LABEL, NAME).


%
% ?????
%
_fch_execution_run(NAME) :- execution_run(NAME).
_fch_execution_run(NAME) :- execution_run(_, NAME).
_fch_ssa(execution_declare(LABEL, NAME, STATEMENTS, INPUT, OUTPUT)) :-
	execution_declare(LABEL, NAME, STATEMENTS, INPUT, OUTPUT),
	_fch_execution_run(NAME).


#defined _fch_enable_optimize_value_output/0.
#defined optimize_value/3.

_fch_optimize_label(LABEL, EXPR_ID, PRIORITY) :- _fch_flat(optimize_label(LABEL, EXPR_ID, PRIORITY)).

%
% ?????
%

%
% variable_default / default_mode.
%
% Only "define" (the default) and "depends" modes have suppression semantics implemented,
% matching what CH's own default tests exercise. "basic" and "none" are accepted as valid
% mode values but currently behave like "define" without the own-assignment suppression.
%
#defined default_mode/1.
_fch_default_possible_mode(basic;define;depends;none).
_fch_default_mode_provided :- default_mode(MODE), _fch_default_possible_mode(MODE).
_fch_default_mode(MODE) :- default_mode(MODE), _fch_default_possible_mode(MODE).
_fch_default_mode(define) :- not _fch_default_mode_provided.

% A default is suppressed once its condition is known to be false.
_fch_default_suppressed(NAME, DEFAULT_ID, COND_ID, PRIORITY) :-
    _fch_var_default(NAME, DEFAULT_ID, COND_ID, PRIORITY),
    _fch_dynamic_expr_val(COND_ID, _fch_type_bool_id, false).

% mode define: a default is suppressed by a direct assignment/definition of the same variable.
_fch_default_suppressed(NAME, DEFAULT_ID, COND_ID, PRIORITY) :-
    _fch_var_default(NAME, DEFAULT_ID, COND_ID, PRIORITY),
    _fch_var_def(NAME, _),
    _fch_default_mode(define).

% mode depends: a default is suppressed if any variable sharing an ensure constraint
% with it (transitively, including itself) is already forced to a value.
_fch_default_expr_var(EXPR_ID, VAR_NAME) :- _fch_expr_var(EXPR_ID, VAR_NAME).
_fch_default_expr_var(EXPR_ID, VAR_NAME) :-
    _fch_op_strict_child(EXPR_ID, CHILD_ID),
    _fch_default_expr_var(CHILD_ID, VAR_NAME).

_fch_default_ensure_var(ENSURE_EXPR_ID, VAR_NAME) :-
    _fch_ensure(_, ENSURE_EXPR_ID),
    _fch_default_expr_var(ENSURE_EXPR_ID, VAR_NAME),
    _fch_default_mode(depends).

_fch_default_connect(X, Y) :-
    _fch_default_ensure_var(ENSURE_EXPR_ID, X),
    _fch_default_ensure_var(ENSURE_EXPR_ID, Y),
    _fch_var_decl(X),
    X != Y.

_fch_default_connect(X, X) :- _fch_var_decl(X), _fch_default_mode(depends).

_fch_default_suppressed(NAME, DEFAULT_ID, COND_ID, PRIORITY) :-
    _fch_var_default(NAME, DEFAULT_ID, COND_ID, PRIORITY),
    _fch_default_connect(NAME, CONNECTED),
    _fch_var_def(CONNECTED, _),
    _fch_default_mode(depends).

_fch_default_apply(NAME, DEFAULT_ID, COND_ID, PRIORITY) :-
    _fch_var_default(NAME, DEFAULT_ID, COND_ID, PRIORITY),
	not _fch_default_suppressed(NAME, DEFAULT_ID, COND_ID, PRIORITY).

% A variable subject to an applying default is defined by the default expression.
_fch_dynamic_var_def(NAME, DEFAULT_ID) :- _fch_default_apply(NAME, DEFAULT_ID, _, _).

%
% CH-facing output compatibility.
%

set_size(NAME, SIZE) :- _fch_set_decl(NAME), _fch_set_size(NAME, SIZE).
set_size(VAR_NAME, SIZE) :- _fch_var_def(VAR_NAME, TARGET_ID), _fch_set_decl(TARGET_ID), _fch_set_size(TARGET_ID, SIZE).

bool_evaluated(EXPR, val(bool, true)) :-
	_fch_bool_evaluate(EXPR, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_bool_id, true).

bool_evaluated(EXPR, val(bool, false)) :-
	_fch_bool_evaluate(EXPR, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_bool_id, false).

bool_evaluated(EXPR, bad) :-
	_fch_bool_evaluate(EXPR, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_fail_id, _).

evaluated(EXPR, val(TYPE, VALUE)) :-
	_fch_evaluate(EXPR, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_none_id, VALUE),
	TYPE = none.

evaluated(EXPR, val(TYPE, VALUE)) :-
	_fch_evaluate(EXPR, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_int_id, VALUE),
	TYPE = int.

evaluated(EXPR, val(float, @fch_legacy_float(INT_PART, REMAINDER))) :-
	_fch_evaluate(EXPR, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_float_id, (INT_PART, REMAINDER)).

evaluated(EXPR, val(TYPE, VALUE)) :-
	_fch_evaluate(EXPR, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_string_id, VALUE),
	TYPE = string.

evaluated(EXPR, val(TYPE, VALUE)) :-
	_fch_evaluate(EXPR, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_bool_id, VALUE),
	TYPE = bool.

evaluated(EXPR, val(TYPE, VALUE)) :-
	_fch_evaluate(EXPR, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_set_id, VALUE),
	TYPE = set.

evaluated(EXPR, val(TYPE, VALUE)) :-
	_fch_evaluate(EXPR, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_dict_id, VALUE),
	TYPE = dict.

evaluated(EXPR, bad) :-
	_fch_evaluate(EXPR, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_fail_id, _).

value(NAME, val(none, none)) :- value(NAME, none, none).
value(NAME, val(int, VALUE)) :- value(NAME, int, VALUE).
value(NAME, val(float, @fch_legacy_float(INT_PART, REMAINDER))) :-
	value(NAME, float, (INT_PART, REMAINDER)).

value(NAME, val(string, VALUE)) :- value(NAME, string, VALUE).
value(NAME, val(bool, VALUE)) :- value(NAME, bool, VALUE).

value(execution_input(EXEC, VAR), VALUE) :- value((EXEC, VAR, in), VALUE).
value(execution_output(EXEC, VAR), VALUE) :- value((EXEC, VAR, out), VALUE).

value((EXEC, VAR, out), none, none) :-
	_fch_flat(execution_output_decl(EXEC, VAR)),
	not _fch_execution_run(EXEC),
	not value((EXEC, VAR, out), bad).

set_value(NAME, val(none, none)) :- set_member(NAME, none, none).
set_value(NAME, val(int, VALUE)) :- set_member(NAME, int, VALUE).
set_value(NAME, val(float, @fch_legacy_float(INT_PART, REMAINDER))) :-
	set_member(NAME, float, (INT_PART, REMAINDER)).

set_value(NAME, val(string, VALUE)) :- set_member(NAME, string, VALUE).
set_value(NAME, val(bool, VALUE)) :- set_member(NAME, bool, VALUE).

set_value(NAME, VALUE) :-
	_fch_var_direct_alias(NAME, TARGET_NAME),
	set_value(TARGET_NAME, VALUE).

set_value(NAME, val(none, none)) :-
	_fch_dynamic_var_def(NAME, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_set_id, SET_ID),
	_fch_set_member(SET_ID, _fch_type_none_id, none).
set_value(NAME, val(int, VALUE)) :-
	_fch_dynamic_var_def(NAME, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_set_id, SET_ID),
	_fch_set_member(SET_ID, _fch_type_int_id, VALUE).
set_value(NAME, val(float, @fch_legacy_float(INT_PART, REMAINDER))) :-
	_fch_dynamic_var_def(NAME, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_set_id, SET_ID),
	_fch_set_member(SET_ID, _fch_type_float_id, (INT_PART, REMAINDER)).
set_value(NAME, val(string, VALUE)) :-
	_fch_dynamic_var_def(NAME, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_set_id, SET_ID),
	_fch_set_member(SET_ID, _fch_type_string_id, VALUE).
set_value(NAME, val(bool, VALUE)) :-
	_fch_dynamic_var_def(NAME, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_set_id, SET_ID),
	_fch_set_member(SET_ID, _fch_type_bool_id, VALUE).

set_value(execution_input(EXEC, VAR), VALUE) :- set_value((EXEC, VAR, in), VALUE).
set_value(execution_output(EXEC, VAR), VALUE) :- set_value((EXEC, VAR, out), VALUE).

value(NAME, bad) :-
	_fch_var_def(NAME, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_fail_id, _).

value(NAME, bad) :-
	_fch_dynamic_var_def(NAME, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_fail_id, _).

_fch_execution_input_declared(EXEC, VAR) :- _fch_flat(var_decl((EXEC, VAR, in))).
_fch_execution_input_defined(EXEC, VAR) :- _fch_flat(var_def((EXEC, VAR, in), _)).
_fch_execution_input_has_domain(EXEC, VAR) :- _fch_flat(var_dom((EXEC, VAR, in), _)).

value((EXEC, VAR, in), bad) :-
	_fch_flat(execution_input_decl(EXEC, VAR)),
	not _fch_execution_input_declared(EXEC, VAR),
	not _fch_execution_input_defined(EXEC, VAR),
	not _fch_execution_input_has_domain(EXEC, VAR).

value(execution_input(EXEC, VAR), bad) :- value((EXEC, VAR, in), bad).
value(execution_output(EXEC, VAR), bad) :- value((EXEC, VAR, out), bad).


#defined warning_forbid/1.
#defined warning_forbid/2.
#defined warning_ignore/1.
#defined warning_ignore/2.

_fch_warning_forbid(KIND) :- warning_forbid(KIND).
_fch_warning_forbid(KIND) :- warning_forbid(_, KIND).
_fch_warning_ignore(KIND) :- warning_ignore(KIND).
_fch_warning_ignore(KIND) :- warning_ignore(_, KIND).

warning(variable(badValue), (), NAME) :- value(NAME, bad).

warning(expression(pythonError), (), (python, EXPR_ID, MESSAGE)) :-
	_fch_op_python_variadic(EXPR_ID, _),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_fail_id, pythonError(MESSAGE)).

warning(variable(emptyDomain), (), NAME) :-
	_fch_empty_var_domain(NAME),
	not _fch_inactive_execution_output(NAME).

:- warning(KIND, INFO, MSG), _fch_warning_forbid(KIND), not _fch_warning_ignore(KIND).

blabla(LABEL, PRIORITY) :-
	_fch_optimize_label(LABEL, EXPR_ID, PRIORITY),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_float_id, _).

% _fch_optimize_value_is_float(LABEL, PRIORITY) :-
% 	_fch_optimize_label(LABEL, _, PRIORITY),
% 	_fch_optimize_precision_value(PRIORITY, PRECISION),
% 	PRECISION != 1.

% optimize_value(LABEL, PRIORITY, val(int, TOTAL)) :-
% 	_fch_enable_optimize_value_output,
% 	not _fch_optimize_value_is_float(LABEL, PRIORITY),
% 	_fch_optimize_label(LABEL, _, PRIORITY),
% 	_fch_optimize_precision_value(PRIORITY, PRECISION),
% 	SCALED_TOTAL = #sum { SCALED, EXPR_ID :
% 		_fch_optimize_label(LABEL, EXPR_ID, PRIORITY),
% 		_fch_optimize_weight_by_expr(EXPR_ID, PRIORITY, SCALED)
% 	},
% 	TOTAL = @fch_unscale_int(SCALED_TOTAL, PRECISION).

% optimize_value(LABEL, PRIORITY, val(float, @fch_legacy_scaled_float(SCALED_TOTAL, PRECISION))) :-
% 	_fch_enable_optimize_value_output,
% 	_fch_optimize_value_is_float(LABEL, PRIORITY),
% 	_fch_optimize_label(LABEL, _, PRIORITY),
% 	_fch_optimize_precision_value(PRIORITY, PRECISION),
% 	SCALED_TOTAL = #sum { SCALED, EXPR_ID :
% 		_fch_optimize_label(LABEL, EXPR_ID, PRIORITY),
% 		_fch_optimize_weight_by_expr(EXPR_ID, PRIORITY, SCALED)
% 	}.

_fch_enable_optimize_value_output.
