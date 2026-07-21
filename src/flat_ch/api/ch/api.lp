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

#defined variable_declareOptional/1.
_fch_input(variable_domain(_fch_label, NAME, val(none, none))) :- variable_declareOptional(NAME).

#defined ensure/1.
#defined ensure/2.
_fch_input(ensure(__anonymous, EXPR)) :- ensure(EXPR).
_fch_input(ensure(LABEL, EXPR)) :- ensure(LABEL, EXPR).

#defined evaluate/2.
#defined evaluate/3.
_fch_input(evaluate(_fch_label, OP, ARGS)) :- evaluate(OP, ARGS).
_fch_input(evaluate(LABEL, OP, ARGS)) :- evaluate(LABEL, OP, ARGS).

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

_fch_optimize_label(LABEL, EXPR_ID, PRIORITY) :- _fch_flat(optimize_label(LABEL, EXPR_ID, PRIORITY)).

%
% ?????
%


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

evaluated(OP, ARGS, val(TYPE, VALUE)) :-
	_fch_evaluate(OP, ARGS, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_none_id, VALUE),
	TYPE = none.

evaluated(OP, ARGS, val(TYPE, VALUE)) :-
	_fch_evaluate(OP, ARGS, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_int_id, VALUE),
	TYPE = int.

evaluated(OP, ARGS, val(float, float(VALUE))) :-
	_fch_evaluate(OP, ARGS, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_float_id, VALUE).

evaluated(OP, ARGS, val(TYPE, VALUE)) :-
	_fch_evaluate(OP, ARGS, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_string_id, VALUE),
	TYPE = string.

evaluated(OP, ARGS, val(TYPE, VALUE)) :-
	_fch_evaluate(OP, ARGS, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_bool_id, VALUE),
	TYPE = bool.

evaluated(OP, ARGS, val(TYPE, VALUE)) :-
	_fch_evaluate(OP, ARGS, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_set_id, VALUE),
	TYPE = set.

evaluated(OP, ARGS, val(TYPE, VALUE)) :-
	_fch_evaluate(OP, ARGS, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_dict_id, VALUE),
	TYPE = dict.

evaluated(OP, ARGS, bad) :-
	_fch_evaluate(OP, ARGS, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_fail_id, _).

value(NAME, val(none, none)) :- value(NAME, none, none).
value(NAME, val(int, VALUE)) :- value(NAME, int, VALUE).
value(NAME, val(float, float(VALUE))) :-
	value(NAME, float, VALUE).

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
set_value(NAME, val(float, float(VALUE))) :-
	set_member(NAME, float, VALUE).

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


#defined warning_forbid/1.
#defined warning_forbid/2.
#defined warning_ignore/1.
#defined warning_ignore/2.

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
