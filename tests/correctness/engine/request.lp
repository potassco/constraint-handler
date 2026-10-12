isEngine(compile;ground;propagator).
isStartEngine(compile;ground).
combo(E1,E2,E3) :- isStartEngine(E1), isStartEngine(E2), isEngine(E3), E1 <= E2.
combo(E3,E2,E3) :- isStartEngine(E2), isEngine(E3), E3=propagator.
combo(E2,E3,E3) :- isStartEngine(E2), isEngine(E3), E3=propagator.
combo(E,E,E)   :- isEngine(E).

variable_define(i(E1,E2,E3),val(int,42),val(bool,true),assign_i(E1,E2,E3)) :- combo(E1,E2,E3).
variable_define(j(E1,E2,E3),val(int,2),val(bool,true),assign_j(E1,E2,E3)) :- combo(E1,E2,E3).
variable_define(y(E1,E2,E3),
    operation(add,
        (operation(mult,
            (variable(j(E1,E2,E3)),
            (variable(i(E1,E2,E3)),()))),
        (val(int,1),()))),
val(bool,true),assign_y(E1,E2,E3)) :- combo(E1,E2,E3).
engine_request(E1,assign_i(E1,E2,E3)) :- combo(E1,E2,E3).
engine_request(E2,assign_j(E1,E2,E3)) :- combo(E1,E2,E3).
engine_request(E3,assign_y(E1,E2,E3)) :- combo(E1,E2,E3).

variable_define(i,val(int,3),val(bool,true),assign_cons_i).
variable_define(j,operation(mult,(variable(i),(variable(i),()))),val(bool,true),assign_cons_j).
variable_define(k,operation(add,(variable(i),(variable(j),()))),val(bool,true),assign_cons_k).
engine_request(compile,assign_cons_i).
engine_request(ground,assign_cons_j).
engine_request(propagator,assign_cons_k).
