execution_declare(
	should_be_ignored,
	if(val(bool,false),statement_python("raise solver_environment.FailIntegrityExn"),assign("x", val(int,1))),
	(),
	("x",())
).

variable_declare(enabled,boolDomain).
variable_define(execution_input(python_check,"ok"),variable(enabled)).
execution_declare(python_check,statement_python("solver_environment.constrain(ok)"),("ok",()),(),variable(enabled)).
execution_declare(python_never,statement_python("raise solver_environment.FailIntegrityExn"),(),(),val(bool,false),python_label).

variable_declare(execution_input(prg2,run),boolDomain).
ensure(operation(lnot,(variable(execution_input(prg2,run)),()))).
execution_declare(
	prg2,
	seq2(
	if(variable(run),statement_python("raise solver_environment.FailIntegrityExn"),noop),assign("x", val(int,2))),
	(run,()),
	("x",())
).

variable_declare(execution_input(prg3,run),boolDomain).
execution_declare(
	prg3,
	seq2(
	if(variable(run),statement_python("raise solver_environment.FailIntegrityExn"),noop),
	assign("x", val(int,3))),
	(run,()),
	("x",())
).

variable_declare(execution_input(prg4,"run"),boolDomain).
execution_declare(
	prg4,
	seq2(
	statement_python("if run:\n  raise solver_environment.FailIntegrityExn"),
	assign("x", val(int,4))),
	("run",()),
	("x",())
).
