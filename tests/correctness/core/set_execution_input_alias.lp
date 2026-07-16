% Regression for compile2/ground going unsat when variables in different namespaces have the same name.

ensure(operation(limp,(val(bool,true),(operation(eq,(variable(b),(variable(execution_input(c,b)),()))),())))).
ensure(operation(limp,(val(bool,true),(operation(eq,(variable(b),(variable(execution_output(prg,b)),()))),())))).

execution_declare(prg,assign(b,operation(set_make,(val(string,"A"),(val(string,"C"),())))),(),(b,())).
execution_run(prg).

variable_declare(b,set).
set_baseDomain(b,val(string,"A")).
set_baseDomain(b,val(string,"C")).

variable_declare(execution_input(c,b),fromFacts).
variable_domain(execution_input(c,b),variable(b)).
