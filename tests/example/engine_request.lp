isEngine(compile;ground;propagator).
isStartEngine(compile;ground).
combo(E1,E2,E3) :- isStartEngine(E1), isStartEngine(E2), isEngine(E3), E1 <= E2.
combo(E3,E2,E3) :- isStartEngine(E2), isEngine(E3), E3=propagator.
combo(E,E,E)   :- isEngine(E).

variable_define(assign_i(E1,E2,E3), i(E1,E2,E3), val(int,42)) :- combo(E1,E2,E3).
variable_define(assign_j(E1,E2,E3), j(E1,E2,E3), val(int,2)) :- combo(E1,E2,E3).
variable_define(assign_y(E1,E2,E3), y(E1,E2,E3), operation(add,(operation(mult,(variable(j(E1,E2,E3)),
                                                  (variable(i(E1,E2,E3)), ()))),
                                  (val(int,1), ())))) :- combo(E1,E2,E3).
requestEngine(assign_i(E1,E2,E3), compile) :- combo(E1,E2,E3).
requestEngine(assign_j(E1,E2,E3), ground) :- combo(E1,E2,E3).
requestEngine(assign_y(E1,E2,E3), propagator) :- combo(E1,E2,E3).

variable_define(assign_cons_i, i, val(int,3)).
variable_define(assign_cons_j, j, operation(mult,(variable(i),(variable(i),())))).
variable_define(assign_cons_k, k, operation(add,(variable(i),(variable(j),())))).
requestEngine(assign_cons_i, compile).
requestEngine(assign_cons_j, ground).
requestEngine(assign_cons_k, propagator).

#show value/2.