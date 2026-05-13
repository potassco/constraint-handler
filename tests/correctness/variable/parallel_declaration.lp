1 { a(0); a(1) } 1.
variable_define(x,val(bool,true)) :- a(0).
variable_define(x,val(bool,false)) :- a(1).

1 { b(0); b(2) } 1.
variable_define(y,val(bool,true)) :- b(0).
variable_define(y,val(bool,false)) :- b(2).

1 { c(0); c(4) } 1.
ensure(operation(leqv,(variable(x),(variable(y),())))) :- c(0).
ensure(operation(lxor,(variable(x),(variable(y),())))) :- c(4).

total(X+Y+Z) :- a(X), b(Y), c(Z).
#show total/1.
