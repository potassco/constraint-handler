variable_declare(y,fromFacts).
variable_domain(y,val(int,-1..3)).

variable_define(execution_input(div0,"x"),val(int,4)).
variable_define(execution_input(div0,"y"),variable(y)).

execution_declare(div0,statement_python("z = x/y\nassert 1.5 < z"),("x",("y",())),()).
execution_run(div0).

{ activate }.
forbid_warning(statement(pythonError)) :- activate.
variable_define(active,val(bool,true)) :- activate.
variable_define(active,val(bool,false)) :- not activate.

variable_define(bad_y,operation(disj,(EQ1,(EQ0,())))) :-
EQ1 = operation(eq,(variable(y),(val(int,-1),()))),
EQ0 = operation(eq,(variable(y),(val(int,0),()))).
variable_define(good_y,GEQ) :-
GEQ = operation(geq,(variable(y),(val(int,1),()))).

evaluate(limp,(variable(active),(variable(good_y),()))).
#show value/2.
#show warning/3.
ignore_warning(type(failed_operation)).
