phase_request(type_check,true).
variable_define(execution_input(prg,"t"),val(int,1)).
variable_define(execution_input(prg,"x"),val(int,2)).
variable_define(execution_input(prg,"y"),val(float,float("4.5"))).
variable_define(execution_input(prg,"z"),val(string,"hel")).

execution_declare(prg,statement_python("t += 7\nx += 2.5\ny -= 2\nz += 'lo'"),("t",("x",("y",("z",())))),("t",("x",("y",("z",()))))).
execution_run(prg).
