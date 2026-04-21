{ more_options }.
variable_declare(x,fromFacts).
variable_domain(x,val(int,7)).
variable_domain(x,val(int,5)) :- more_options.

variable_define(execution_input(add_one,x),variable(x)).
execution_declare(add_one,assign(y,operation(add,(variable(x),(val(int,1),())))),(x,()),(y,())).
execution_run(add_one) :- not more_options.

variable_define(y,operation(default,(variable(execution_output(add_one,y)),(val(int,10),())))).
variable_define(h,operation(hasValue,(variable(y),()))).

#show value/2.
