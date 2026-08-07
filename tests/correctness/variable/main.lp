variable_declare(x,boolDomain).
variable_define(y,operation(lnot,(variable(x),()))).
evaluate(neq,(variable(x),(variable(y),()))).

variable_declare(r,fromFacts).
variable_domain(r,R) :-
  R=val(symbol,red).
variable_declare(g,fromFacts).
variable_domain(g,C) :-
  C=val(symbol,(red;green;blue)).
variable_declare(b,fromFacts).
variable_domain(b,val(symbol,(red;green;blue))).

variable_declare(p,fromFacts).
variable_domain(p,C) :-
  C=val(symbol,(red;green;blue)).
variable_domain(p,val(none,none)).

ensure(operation(eq,(variable(b),(val(symbol,blue),())))).
ensure(operation(neq,(variable(r),(variable(g),())))).
ensure(operation(neq,(variable(g),(variable(b),())))).

ensure(operation(neq,(variable(r),(variable(p),())))).
ensure(operation(neq,(variable(g),(variable(p),())))).
ensure(operation(neq,(variable(b),(variable(p),())))).

variable_define(g_is_green,operation(eq,(variable(g),(val(symbol,green),())))).
