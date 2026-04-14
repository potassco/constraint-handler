% Regression: set_isin/set_notin should agree with python fallback membership via statement_python.

variable_define(pool,operation(set_make,(val(str,"X"),(val(str,"Y"),())))).

execution_declare(py_membership,
	statement_python("py_in = x in ['X', 'Y']\npy_not = x not in ['X', 'Y']"),
	("x",()),
	("py_in",("py_not",()))).

variable_declare(execution_input(py_membership,"x"),fromFacts).
variable_domain(execution_input(py_membership,"x"),val(str,"X")).
variable_domain(execution_input(py_membership,"x"),val(none,none)).

execution_run(py_membership).

evaluate(set_isin,(variable(execution_input(py_membership,"x")),(variable(pool),()))).
evaluate(set_notin,(variable(execution_input(py_membership,"x")),(variable(pool),()))).
evaluate(eq,
	(operation(set_isin,(variable(execution_input(py_membership,"x")),(variable(pool),()))),
	(variable(execution_output(py_membership,"py_in")),()))).
evaluate(eq,
	(operation(set_notin,(variable(execution_input(py_membership,"x")),(variable(pool),()))),
	(variable(execution_output(py_membership,"py_not")),()))).
