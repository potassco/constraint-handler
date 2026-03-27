variable_declare(y,fromFacts).
variable_domain(y,val(int,0..2)).

variable_define(execution_input(div0,"y"),variable(y)).


execution_declare(div0,statement_python("z = 4/y\nsolver_environment.constrain(z != 2)"),("y",()),()).
execution_run(div0).

{ never }.
:- never.
forbid_warning(statement(pythonError)) :- never.
#show value/2.
