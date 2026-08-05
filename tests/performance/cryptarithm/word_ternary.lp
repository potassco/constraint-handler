% SEND + MORE = MONEY
letter(s;e;n;d;m;o;r;y).
leading(s;m).

variable_declare(L,fromFacts) :- letter(L).
variable_domain(L,val(int,1..9)) :- leading(L).
variable_domain(L,val(int,0..9)) :- letter(L), not leading(L).

ensure(operation(neq,(variable(L1),(variable(L2),())))) :- letter(L1), letter(L2), L1 < L2.

variable_define(send,operation(add,(operation(mult,(val(int,1000),(variable(s),()))),(operation(mult,(val(int,100),(variable(e),()))),(operation(add,(operation(mult,(val(int,10),(variable(n),()))),(variable(d),()))),()))))).
variable_define(more,operation(add,(operation(mult,(val(int,1000),(variable(m),()))),(operation(mult,(val(int,100),(variable(o),()))),(operation(add,(operation(mult,(val(int,10),(variable(r),()))),(variable(e),()))),()))))).
variable_define(money,operation(add,(operation(mult,(val(int,10000),(variable(m),()))),(operation(mult,(val(int,1000),(variable(o),()))),(operation(add,(operation(mult,(val(int,100),(variable(n),()))),(operation(add,(operation(mult,(val(int,10),(variable(e),()))),(variable(y),()))),()))),()))))).

ensure(operation(eq,(operation(add,(variable(send),(variable(more),()))),(variable(money),())))).
