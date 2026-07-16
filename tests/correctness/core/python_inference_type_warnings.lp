phase_request(type_check,true).

variable_define(extract_list,operation(pythonExtract("tmp=[1,2,3]","tmp"),())).

execution_declare(py_warn,
    statement_python("y = [1, 2, 3]"),
    (),
    ("y",())).
execution_run(py_warn).

variable_define(extract_obj,operation(pythonExtract("tmp=object()","tmp"),())).

execution_declare(py_obj,
    statement_python("y = object()"),
    (),
    ("y",())).
execution_run(py_obj).
