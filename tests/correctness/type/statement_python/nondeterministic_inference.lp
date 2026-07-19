phase_request(type_check,true).

execution_declare(py_nd,
    statement_python("y = x"),
    ("x",()),
    ("y",())).

variable_declare(execution_input(py_nd,"x"),fromFacts).
variable_domain(execution_input(py_nd,"x"),val(int,2)).
variable_domain(execution_input(py_nd,"x"),val(string,"two")).

execution_run(py_nd).
