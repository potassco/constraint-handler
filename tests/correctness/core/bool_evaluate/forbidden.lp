variable(x).
variable_declare(X,fromFacts) :- variable(X).
variable_domain(X,val(int,1..3)) :- variable(X).

isn(operation(eq,(variable(X),(val(int,N),()))),X,N) :- variable(X), N=1..3.
bool_evaluate(E) :- isn(E,X,N).

{ play_safe }.
bool_evaluated(E,val(int,73)) :- isn(E,x,1), not play_safe.
