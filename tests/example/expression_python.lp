variable_define(x,python("2")).
variable_define(y,operation(sub,(variable(x),(python("3"),())))).
variable_define(z,operation(python("abs"),(variable(y),()))).

#show value/2.
#show warning/3.
#show _se_value/2.
#show _se_assign/2.
#show direct_query/1.