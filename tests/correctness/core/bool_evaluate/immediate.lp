variable(x;y).
variable_declare(X,fromFacts) :- variable(X).
variable_domain(X,val(int,1..3)) :- variable(X).

isn(operation(eq,(variable(X),(val(int,N),()))),X,N) :- variable(X), N=1..3.
bool_evaluate(E) :- isn(E,X,N).

:- bool_evaluated(E,val(bool,true)), isn(E,x,1).
:- bool_evaluated(E,val(bool,true)), isn(E,x,2).

is_3(x) :- bool_evaluated(E,val(bool,true)), isn(E,x,3).

:- bool_evaluated(E,val(bool,false)), isn(E,y,3).

is_3(y) :- bool_evaluated(E,val(bool,true)), isn(E,y,3).
