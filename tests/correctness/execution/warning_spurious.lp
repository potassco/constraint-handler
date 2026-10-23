execution_declare(example,statement_python("1 ++"),(),(),variable(run)).
variable_declare(run,boolDomain).
warning_forbid(expression(pythonError)).