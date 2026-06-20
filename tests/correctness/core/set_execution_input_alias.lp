% Regression for compile2/ground going unsat when a set-valued execution input
% is aliased to a multivalue property that is also assigned via an execution.

ensure((cv2,(execution_input(c,b),b)),operation(limp,(val(bool,true),(operation(eq,(variable(b),(variable(execution_input(c,b)),()))),())))).
ensure((cv2,(execution_output(a,b),b)),operation(limp,(val(bool,true),(operation(eq,(variable(b),(variable(execution_output(a,b)),()))),())))).

execution_declare(a,a,assign(b,operation(set_make,(val(string,"A"),(val(string,"C"),())))),(),(b,())).
execution_run(a,a).

set_baseDomain(b,b,val(string,"A")).
set_baseDomain(b,b,val(string,"C")).
set_declare(b,b).

variable_domain(execution_input(c,b),variable(b)).
