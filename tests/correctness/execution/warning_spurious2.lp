execution_declare(example,statement_python("x = 3 if cond else 5/0"),("cond",()),("x",()),variable(run)).
variable_declare(run,boolDomain).
variable_declare(execution_input(example,"cond"),boolDomain).
warning_forbid(expression(pythonError)).
