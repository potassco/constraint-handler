%
% Additional CH-facing API declarations.
% This file only forwards legacy CH arities that are not already covered by encodings/api.lp.
%

#defined variable_declare/2.
_fch_input(variable_declare(NAME, DOMAIN)) :- variable_declare(NAME, DOMAIN).

#defined variable_declare/3.
_fch_input(variable_declare(SCOPE, NAME, DOMAIN)) :- variable_declare(SCOPE, NAME, DOMAIN).

#defined variable_define/3.
_fch_input(variable_define(LABEL, NAME, EXPR)) :- variable_define(LABEL, NAME, EXPR).

#defined warning_forbid/1.
#defined warning_forbid/2.
#defined warning_ignore/1.
#defined warning_ignore/2.

#defined evaluate/2.
_fch_input(evaluate(OP, ARGS)) :- evaluate(OP, ARGS).

#defined evaluate/3.
_fch_input(evaluate(LABEL, OP, ARGS)) :- evaluate(LABEL, OP, ARGS).

#defined bool_evaluate/2.
_fch_input(bool_evaluate(LABEL, EXPR)) :- bool_evaluate(LABEL, EXPR).

#defined set_declare/2.
_fch_input(set_declare(SCOPE, NAME)) :- set_declare(SCOPE, NAME).

#defined set_baseDomain/3.
_fch_input(set_baseDomain(SCOPE, NAME, EXPR)) :- set_baseDomain(SCOPE, NAME, EXPR).

#defined set_assign/3.
_fch_input(set_assign(SCOPE, NAME, EXPR)) :- set_assign(SCOPE, NAME, EXPR).

#defined optimize_maximizeSum/2.
_fch_input(optimize_maximizeSum(EXPR, ELEMENT, 0)) :- optimize_maximizeSum(EXPR, ELEMENT).

#defined optimize_maximizeSum/4.
_fch_input(optimize_maximizeSum(LABEL, EXPR, ELEMENT, PRIORITY)) :- optimize_maximizeSum(LABEL, EXPR, ELEMENT, PRIORITY).

#defined _fch_enable_optimize_value_output/0.

_fch_optimize_label(LABEL, EXPR_ID, PRIORITY) :- _fch_flat(optimize_label(LABEL, EXPR_ID, PRIORITY)).

#defined execution_declare/5.
#defined execution_declare/4.
_fch_execution_decl_meta(execution_declare(NAME, LABEL, STATEMENTS, INPUT, OUTPUT)) :- execution_declare(NAME, LABEL, STATEMENTS, INPUT, OUTPUT).
#defined execution_run/2.
_fch_execution_run(NAME) :- execution_run(NAME, _).
_fch_ssa(execution_declare(NAME, LABEL, STATEMENTS, INPUT, OUTPUT)) :-
	execution_declare(NAME, LABEL, STATEMENTS, INPUT, OUTPUT),
	_fch_execution_run(NAME).

%
% CH-facing output compatibility.
%

value(NAME, val(none, none)) :- value(NAME, none, none).
value(NAME, val(int, VALUE)) :- value(NAME, int, VALUE).
value(NAME, val(float, float(VALUE))) :- value(NAME, float, VALUE).
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
set_value(NAME, val(float, float(VALUE))) :- set_member(NAME, float, VALUE).
set_value(NAME, val(string, VALUE)) :- set_member(NAME, string, VALUE).
set_value(NAME, val(bool, VALUE)) :- set_member(NAME, bool, VALUE).

set_value(NAME, val(none, none)) :-
	_fch_dynamic_var_def(NAME, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_set_id, SET_ID),
	_fch_set_member(SET_ID, _fch_type_none_id, none).
set_value(NAME, val(int, VALUE)) :-
	_fch_dynamic_var_def(NAME, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_set_id, SET_ID),
	_fch_set_member(SET_ID, _fch_type_int_id, VALUE).
set_value(NAME, val(float, float(VALUE))) :-
	_fch_dynamic_var_def(NAME, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_set_id, SET_ID),
	_fch_set_member(SET_ID, _fch_type_float_id, VALUE).
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

evaluated(OP, ARGS, val(float, float(VALUE))) :-
    _fch_evaluate(OP, ARGS, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, _fch_type_float_id, VALUE).

value(NAME, bad) :-
	_fch_var_def(NAME, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_fail_id, _).

value(NAME, bad) :-
	_fch_dynamic_var_def(NAME, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_fail_id, _).

value((EXEC, VAR, in), bad) :-
	_fch_flat(execution_input_decl(EXEC, VAR)),
	not _fch_flat(var_decl((EXEC, VAR, in))),
	not _fch_flat(var_def((EXEC, VAR, in), _)),
	not _fch_flat(var_dom((EXEC, VAR, in), _)).

value(execution_input(EXEC, VAR), bad) :- value((EXEC, VAR, in), bad).
value(execution_output(EXEC, VAR), bad) :- value((EXEC, VAR, out), bad).

_fch_warning_forbid(KIND) :- warning_forbid(KIND).
_fch_warning_forbid(KIND) :- warning_forbid(_, KIND).
_fch_warning_ignore(KIND) :- warning_ignore(KIND).
_fch_warning_ignore(KIND) :- warning_ignore(_, KIND).

warning(variable(badValue), (), NAME) :- value(NAME, bad).

:- warning(KIND, INFO, MSG), _fch_warning_forbid(KIND), not _fch_warning_ignore(KIND).

_fch_optimize_value_is_float(LABEL, PRIORITY) :-
	_fch_optimize_label(LABEL, EXPR_ID, PRIORITY),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_float_id, _).

_fch_optimize_value_is_float(LABEL, PRIORITY) :-
	_fch_optimize_label(LABEL, _, PRIORITY),
	_fch_optimize_precision_value(PRIORITY, PRECISION),
	PRECISION != 1.

optimize_value(LABEL, PRIORITY, val(int, TOTAL)) :-
	_fch_enable_optimize_value_output,
	not _fch_optimize_value_is_float(LABEL, PRIORITY),
	_fch_optimize_label(LABEL, _, PRIORITY),
	_fch_optimize_precision_value(PRIORITY, PRECISION),
	SCALED_TOTAL = #sum { SCALED, EXPR_ID :
		_fch_optimize_label(LABEL, EXPR_ID, PRIORITY),
		_fch_optimize_weight_by_expr(EXPR_ID, PRIORITY, SCALED)
	},
	TOTAL = @fch_unscale_int(SCALED_TOTAL, PRECISION).

optimize_value(LABEL, PRIORITY, val(float, float(VALUE))) :-
	_fch_enable_optimize_value_output,
	_fch_optimize_value_is_float(LABEL, PRIORITY),
	_fch_optimize_label(LABEL, _, PRIORITY),
	_fch_optimize_precision_value(PRIORITY, PRECISION),
	SCALED_TOTAL = #sum { SCALED, EXPR_ID :
		_fch_optimize_label(LABEL, EXPR_ID, PRIORITY),
		_fch_optimize_weight_by_expr(EXPR_ID, PRIORITY, SCALED)
	},
	VALUE = @fch_scaled_int_to_float(SCALED_TOTAL, PRECISION).
