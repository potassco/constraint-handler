phase_request(type_check,true).

execution_declare(py_nd_mix,
    statement_python("y = 1 if gate else [1, 2]"),
    ("gate",()),
    ("y",())).

variable_declare(execution_input(py_nd_mix,"gate"),fromFacts).
variable_domain(execution_input(py_nd_mix,"gate"),val(bool,true)).
variable_domain(execution_input(py_nd_mix,"gate"),val(bool,false)).

execution_run(py_nd_mix).

variable_define(output_add,
    operation(add,(variable(execution_output(py_nd_mix,"y")),(val(string,"s"),())))).
