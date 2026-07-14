execution_run(should_be_ignored).

execution_declare(
	should_be_ignored,
	if(val(bool,false),statement_python("raise solver_environment.FailIntegrityExn"),assign("x", val(int,1))),
	(),
	("x",())
).