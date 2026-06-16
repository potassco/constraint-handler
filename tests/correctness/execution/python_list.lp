execution_declare(prg1,statement_python("l = [1,2,3]\nx = sum(l)"),(),("x",())).
execution_run(prg1).
evaluate(eq,(variable(execution_output(prg1,"x")),(val(int,6),()))).

execution_declare(prg2,statement_python("l = list([1,2,3])\nx = sum(l)"),(),("x",())).
execution_run(prg2).
evaluate(eq,(variable(execution_output(prg2,"x")),(val(int,6),()))).

execution_declare(prg3,statement_python("l = set([1,2,3])\nx = sum(l)"),(),("x",())).
execution_run(prg3).
evaluate(eq,(variable(execution_output(prg3,"x")),(val(int,6),()))).
