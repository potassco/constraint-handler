variable_define(execution_input(prg,"x"),val(int,1)).

execution_declare(prg,statement_python("x += 2.5"),("x",()),("x",())).
execution_run(prg).
