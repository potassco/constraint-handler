% Compile emits an expression(pythonError) warning for the extracted
% statement_python call; compile2 currently drops that warning.

variable_declare(a,a,fromFacts).
variable_domain(a,val(int,1)).
variable_domain(a,val(int,4)).

variable_declare(execution_input(p,"a"),execution_input(p,"a"),fromFacts).
variable_domain(execution_input(p,"a"),variable(a)).

ensure(operation(limp,(val(bool,true),(operation(eq,(variable(execution_input(p,"a")),(variable(a),()))),())))).

execution_declare(p,if(operation(eq,(variable("a"),(val(int,4),()))),statement_python("assert(False)"),noop),("a",()),()).
execution_run(p).

evaluate(eq,(variable(a),(val(int,4),()))).
