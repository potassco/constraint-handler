variable_define(execution_input(prg(all),"t"),val(int,1)).
variable_define(execution_input(prg(all),"x"),val(string,"helllo")).
variable_define(execution_input(prg(all),"y"),val(float,float("4.5"))).

variable_define(execution_input(prg(t),"t"),val(int,1)).
variable_define(execution_input(prg(y),"y"),val(float,float("4.5"))).

execution_declare(prg(all),statement_python("y += 2\nt += 'hello'\nx -= 'lo'"),("t",("x",("y",()))),("t",("x",("y",())))).
execution_run(prg(all)).
execution_declare(prg(y),statement_python("y += 2"),("y",()),("y",())).
execution_run(prg(y)).
execution_declare(prg(t),statement_python("t += 'hello'"),("t",()),("t",())).
execution_run(prg(t)).
