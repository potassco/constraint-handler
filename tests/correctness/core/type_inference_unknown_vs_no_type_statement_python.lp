execution_declare(py_mix,
    statement_python("y=[1,2,3]"),
    (),
    ("y",())).

execution_run(py_mix).

variable_define(output_add,
    operation(add,(variable(execution_output(py_mix,"y")),(val(int,1),())))).
