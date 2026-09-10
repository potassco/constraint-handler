isEngine(compile;ground;propagator).
isStartEngine(compile;ground).
combo(E1,E2,E3) :- isStartEngine(E1), isStartEngine(E2), isEngine(E3), E1 <= E2.
combo(E3,E2,E3) :- isStartEngine(E2), isEngine(E3), E3=propagator.
combo(E2,E3,E3) :- isStartEngine(E2), isEngine(E3), E3=propagator.
combo(E,E,E)   :- isEngine(E).

variable_define(i(E1,E2,E3),val(int,42),assign_i(E1,E2,E3)) :- combo(E1,E2,E3).
variable_define(j(E1,E2,E3),val(int,2),assign_j(E1,E2,E3)) :- combo(E1,E2,E3).
variable_define(y(E1,E2,E3),
    operation(add,
        (operation(mult,
            (variable(j(E1,E2,E3)),
            (variable(i(E1,E2,E3)),()))),
        (val(int,1),()))),
assign_y(E1,E2,E3)) :- combo(E1,E2,E3).
engine_request(assign_i(E1,E2,E3),E1) :- combo(E1,E2,E3).
engine_request(assign_j(E1,E2,E3),E2) :- combo(E1,E2,E3).
engine_request(assign_y(E1,E2,E3),E3) :- combo(E1,E2,E3).

variable_define(i,val(int,3),assign_cons_i).
variable_define(j,operation(mult,(variable(i),(variable(i),()))),assign_cons_j).
variable_define(k,operation(add,(variable(i),(variable(j),()))),assign_cons_k).
engine_request(assign_cons_i,compile).
engine_request(assign_cons_j,ground).
engine_request(assign_cons_k,propagator).
