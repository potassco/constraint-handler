phase_request(type_check,true).

variable_declare(raw,fromFacts).
variable_domain(raw,val(int,7)).
variable_domain(raw,val(bool,true)).

variable_define(extract_out,operation(pythonExtract("tmp = raw","tmp"),((val(string,"raw"),variable(raw)),()))).

execution_declare(py_nd,
    statement_python("y = x"),
    ("x",()),
    ("y",())).

variable_declare(execution_input(py_nd,"x"),fromFacts).
variable_domain(execution_input(py_nd,"x"),val(int,2)).
variable_domain(execution_input(py_nd,"x"),val(string,"two")).

execution_run(py_nd).
