variable_define(n,val(int,3)).
variable_define(execution_input(makeList,"n"),variable(n)).
variable_define(execution_input(makeSet,"n"),variable(n)).
variable_define(b,variable(execution_output(makeList,"b"))).
variable_define(c,variable(execution_output(makeSet,"c"))).

execution_declare(makeList,statement_python("a = range(n)\nb = list(a)"),("n",()),("b",())).
execution_declare(makeSet,statement_python("a = range(n)\nc = set(a)"),("n",()),("c",())).
%{ execution_run(makeList) }.
%warning_forbid(expression(pythonError)).
execution_run(makeList).
execution_run(makeSet).

#show warning/3.
#show value/2.
#show set_value/2.
#show _ge_assign/3.
#show _ge_eval_exec/3.
