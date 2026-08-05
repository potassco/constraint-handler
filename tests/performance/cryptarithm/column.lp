% SEND + MORE = MONEY
letter(s;e;n;d;m;o;r;y).
leading(s;m).

variable_declare(L,fromFacts) :- letter(L).
variable_domain(L,val(int,1..9)) :- leading(L).
variable_domain(L,val(int,0..9)) :- letter(L), not leading(L).

ensure(operation(neq,(variable(L1),(variable(L2),())))) :- letter(L1), letter(L2), L1 < L2.

carry(c1;c2;c3;c4).

variable_declare(C,fromFacts) :- carry(C).
variable_domain(C,val(int,0..1)) :- carry(C).

ensure(operation(eq,(operation(add,(variable(d),(variable(e),()))),(operation(add,(variable(y),(operation(mult,(val(int,10),(variable(c1),()))),()))),())))).
ensure(operation(eq,(operation(add,(variable(n),(variable(r),(variable(c1),())))),(operation(add,(variable(e),(operation(mult,(val(int,10),(variable(c2),()))),()))),())))).
ensure(operation(eq,(operation(add,(variable(e),(variable(o),(variable(c2),())))),(operation(add,(variable(n),(operation(mult,(val(int,10),(variable(c3),()))),()))),())))).
ensure(operation(eq,(operation(add,(variable(s),(variable(m),(variable(c3),())))),(operation(add,(variable(o),(operation(mult,(val(int,10),(variable(c4),()))),()))),())))).
ensure(operation(eq,(variable(c4),(variable(m),())))).
