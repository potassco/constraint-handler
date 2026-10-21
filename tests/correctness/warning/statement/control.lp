phase_request(statement_wellformedCheck,true).

execution_declare(control_lists_ok,
	noop,
	(inp,()),
	(out,()),
	val(bool,false)
).

execution_declare(control_nested_ok,
	seq2(
		assign(out,operation(add,(val(int,1),(val(int,2),())))),
		if(
			operation(eq,(val(int,1),(val(int,1),()))),
			seq2(
				assert(operation(eq,(val(int,3),(val(int,3),())))),
				statement_python("z=1")
			),
			noop
		)
	),
	(inp,()),
	(out,(inp,())),
	val(bool,false)
).

#show warning/3.
