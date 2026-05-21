%%% raises warning(variable(undeclared),(),missing_input).
variable_define(anchor,val(int,1)).
variable_define(leaky,
    operation(pythonExtract("pass","lhs"),((val(string,"lhs"),variable(missing_input)),()))).

variable_define(n,val(int,3)).
%variable_define(execution_input(makeSet,"n"),variable(n)).
variable_define(c,variable(execution_output(prg2,"c"))).

execution_declare(prg,statement_python("a = range(n)\nc = set(a)"),("n",()),("c",())).
execution_run(prg).

#show warning/3.
