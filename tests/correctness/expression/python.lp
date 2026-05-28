variable_define(x,python("2")).
variable_define(y,operation(sub,(variable(x),(python("3"),())))).
variable_define(z,operation(python("abs"),(variable(y),()))).

#show value/2.
#show warning/3.
