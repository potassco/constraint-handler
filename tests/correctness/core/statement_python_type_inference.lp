phase_request(type_check,true).

execution_declare(py_stmt,
    statement_python("y = x + 1\nis_three = y == 3"),
    ("x",()),
    ("y",("is_three",()))).

variable_declare(execution_input(py_stmt,"x"),fromFacts).
variable_domain(execution_input(py_stmt,"x"),val(int,2)).

execution_run(py_stmt).
