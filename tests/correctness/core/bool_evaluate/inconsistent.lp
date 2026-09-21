variable(x).
variable_declare(X,fromFacts) :- variable(X).
variable_domain(X,val(int,1..3)) :- variable(X).

isn(operation(eq,(variable(X),(val(int,N),()))),X,N) :- variable(X), N=1..3.
bool_evaluate(E) :- isn(E,X,N).

bool_evaluated(E,val(bool,true)) :- isn(E,x,3).
isnt(x,N) :- not bool_evaluated(E,val(bool,true)), isn(E,x,N), N=1..2.
