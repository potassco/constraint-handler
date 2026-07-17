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

#show warning/3.