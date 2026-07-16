phase_request(type_check,true).

set_declare(xset,xset).
variable_define(execution_input(prg,"x"),variable(xset)).

execution_declare(prg,statement_python("result = set(x) == set([])"),("x",()),("result",())).
execution_run(prg).
evaluate(eq,(variable(execution_output(prg,"result")),(val(bool,true),()))).
