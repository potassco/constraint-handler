{ a }.

variable_define(x,val(bool,true)) :- a.
variable_define(x,val(bool,false)) :- not a.
ensure(variable(x)).

evaluate(lnot,(variable(x),())) :- a.
evaluate(snot,(variable(x),())) :- not a.
