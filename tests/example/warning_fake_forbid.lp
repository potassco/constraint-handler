variable_declare(dummy,y,fromFacts).
variable_domain(y,val(int,0..2)).

variable_define(dummy,execution_input(div0,"y"),variable(y)).


execution_declare(dummy,div0,statement_python("z = 4/y\nsolver_environment.constrain(z != 2)"),("y",()),()).
execution_run(dummy,div0).

{ never }.
:- never.
forbid_warning(dummy,statement(pythonError)) :- never.
#show value/2.