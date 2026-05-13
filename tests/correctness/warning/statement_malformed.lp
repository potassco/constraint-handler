execution_declare(malformed_stmt_unknown,broken_statement,(),()).

execution_declare(malformed_stmt_assign,
	assign(out,varrriable(x)),
	(),
	(out,())
).

execution_declare(malformed_stmt_assert,
	assert(vaaal(int,1)),
	(),
	()
).

execution_declare(malformed_stmt_if_expr,
	if(varrriable(cond),noop,noop),
	(),
	()
).

execution_declare(malformed_stmt_if_then,
	if(variable(cond),broken_then,noop),
	(),
	()
).

execution_declare(malformed_stmt_if_else,
	if(variable(cond),noop,broken_else),
	(),
	()
).

execution_declare(malformed_stmt_while_expr,
	while(5,varrriable(cond),noop),
	(),
	()
).

execution_declare(
	malformed_stmt_while_body,
	while(5,variable(cond),broken_body),
	(),
	()
).

execution_declare(malformed_stmt_seq2,
	seq2(noop,broken_seq_part),
	(),
	()
).

execution_declare(malformed_stmt_substmt_is_expression,
	seq2(noop,operation(add,(val(int,1),(val(int,2),())))),
	(),
	()
).

execution_declare(malformed_stmt_expr_is_statement,
	assign(out,noop),
	(),
	(out,())
).

execution_declare(malformed_stmt_python,
	statement_python(val(int,1)),
	(),
	()
).

execution_declare(malformed_decl_inputs_not_list,
	noop,
	bad_inputs,
	()
).

execution_declare(malformed_decl_outputs_not_list,
	noop,
	(),
	bad_outputs
).

execution_declare(malformed_decl_both_not_list,
	noop,
	bad_inputs2,
	bad_outputs2
).

execution_declare(control_lists_ok,
	noop,
	(inp,()),
	(out,())
).

execution_declare(control_nested_ok,
	seq2(
		assign(out,operation(add,(val(int,1),(val(int,2),())))),
		if(
			operation(eq,(val(int,1),(val(int,1),()))),
			while(
				2,
				operation(lt,(val(int,0),(val(int,1),()))),
				seq2(
					assert(operation(eq,(val(int,3),(val(int,3),())))),
					statement_python("z=1")
				)
			),
			noop
		)
	),
	(inp,()),
	(out,(inp,()))
).

#show warning/3.
