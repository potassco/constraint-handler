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

#show warning/3.
