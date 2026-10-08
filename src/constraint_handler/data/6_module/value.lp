ch_post(variable_interface(X,LBL)) :- ch_core(variable_declare(X,D),LBL), #false: X=loc(V).
propagator_variable_interface(X,LBL) :- ch_core(variable_declare(X,D),LBL), #false: X=loc(V).
