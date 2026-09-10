phase_request(type_check,true).

variable_declare(xset,set).
variable_define(execution_input(prg,"x"),variable(xset)).

execution_declare(prg,statement_python("result = set(x) == set([])"),("x",()),("result",())).
execution_run(prg).
evaluate(operation(eq,(variable(execution_output(prg,"result")),(val(bool,true),())))).
