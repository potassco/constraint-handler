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

#defined optimize_maximizeSum/4.
_fch_input(optimize_maximizeSum(LABEL, EXPR, ELEMENT, PRIORITY)) :- optimize_maximizeSum(LABEL, EXPR, ELEMENT, PRIORITY).

#defined execution_declare/5.
_fch_ssa(execution_declare(NAME, LABEL, STATEMENTS, INPUT, OUTPUT)) :- execution_declare(NAME, LABEL, STATEMENTS, INPUT, OUTPUT).

%
% CH-facing output compatibility.
%

value(NAME, val(none, none)) :- value(NAME, none, none).
value(NAME, val(int, VALUE)) :- value(NAME, int, VALUE).
value(NAME, val(float, float(VALUE))) :- value(NAME, float, VALUE).
value(NAME, val(string, VALUE)) :- value(NAME, string, VALUE).
value(NAME, val(bool, VALUE)) :- value(NAME, bool, VALUE).

value(NAME, bad) :-
	_fch_var_def(NAME, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_fail_id, _).

value(NAME, bad) :-
	_fch_dynamic_var_def(NAME, EXPR_ID),
	_fch_dynamic_expr_val(EXPR_ID, _fch_type_fail_id, _).
