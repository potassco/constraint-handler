execution_run(should_be_ignored).

execution_declare(
	should_be_ignored,
	if(val(bool,false),statement_python("raise solver_environment.FailIntegrityExn"),assign("x", val(int,1))),
	(),
	("x",())
).

variable_declare(execution_input(prg2,run),boolDomain).
ensure(operation(lnot,(variable(execution_input(prg2,run)),()))).
execution_run(prg2).
execution_declare(
	prg2,
	seq2(
	if(variable(run),statement_python("raise solver_environment.FailIntegrityExn"),noop),assign("x", val(int,2))),
	(run,()),
	("x",())
).

variable_declare(execution_input(prg3,run),boolDomain).
execution_run(prg3).
execution_declare(
	prg3,
	seq2(
	if(variable(run),statement_python("raise solver_environment.FailIntegrityExn"),noop),
	assign("x", val(int,3))),
	(run,()),
	("x",())
).

variable_declare(execution_input(prg4,"run"),boolDomain).
execution_run(prg4).
execution_declare(
	prg4,
	seq2(
	statement_python("if run:\n  raise solver_environment.FailIntegrityExn"),
	assign("x", val(int,4))),
	("run",()),
	("x",())
).
