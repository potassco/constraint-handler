% Regression: set_isin/set_notin should agree with python fallback membership via statement_python.

variable_define(pool,operation(set_make,(val(str,"X"),(val(str,"Y"),())))).
variable_define(pool2,operation(set_make,(val(none,none),(val(str,"Y"),())))).
variable_declare(x,fromFacts).
variable_domain(x,val(str,"X")).
variable_domain(x,val(none,none)).

execution_declare(py_membership,
	statement_python("py_in = x in pool\npy_not = x not in pool"),
	("x",("pool",())),
	("py_in",("py_not",()))).
execution_declare(py_membership2,
	statement_python("py_in = x in pool\npy_not = x not in pool"),
	("x",("pool",())),
	("py_in",("py_not",()))).

variable_define(execution_input(py_membership,"pool"),variable(pool)).
variable_define(execution_input(py_membership,"x"),variable(x)).
variable_define(py_in,variable(execution_output(py_membership,"py_in"))).
variable_define(py_not,variable(execution_output(py_membership,"py_not"))).

execution_run(py_membership).

variable_define(execution_input(py_membership2,"pool"),variable(pool2)).
variable_define(execution_input(py_membership2,"x"),variable(x)).
variable_define(py_in2,variable(execution_output(py_membership2,"py_in"))).
variable_define(py_not2,variable(execution_output(py_membership2,"py_not"))).

execution_run(py_membership2).

evaluate(set_isin,(variable(x),(variable(pool),()))).
evaluate(set_notin,(variable(x),(variable(pool),()))).
evaluate(eq,
	(operation(set_isin,(variable(x),(variable(pool),()))),
	(variable(py_in),()))).
evaluate(eq,
	(operation(set_notin,(variable(x),(variable(pool),()))),
	(variable(py_not),()))).

evaluate(eq,(variable(py_in),(variable(py_in2),()))).
evaluate(eq,(variable(py_not),(variable(py_not2),()))).
