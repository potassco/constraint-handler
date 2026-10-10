evaluated(REF,V) :- ch_post(evaluate(REF,E),LBL), _shared_value(E,V).
evaluated(REF,bad) :- ch_post(evaluate(REF,E),LBL), #false: _shared_value(E,V).
