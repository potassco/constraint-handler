phase_request(type_check,true).

execution_declare(py_warn,
    statement_python("y = [1, 2, 3]"),
    (),
    ("y",())).
execution_run(py_warn).

execution_declare(py_obj,
    statement_python("y = object()"),
    (),
    ("y",())).
execution_run(py_obj).
