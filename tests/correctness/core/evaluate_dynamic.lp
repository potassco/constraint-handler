{ a }.

variable_define(x,val(bool,true)) :- a.
variable_define(x,val(bool,false)) :- not a.
ensure(variable(x)).

evaluate(operation(lnot,(variable(x),()))) :- a.
evaluate(operation(snot,(variable(x),()))) :- not a.
