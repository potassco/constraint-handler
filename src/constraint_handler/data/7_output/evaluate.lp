evaluated(REF,V) :- ch_post(evaluate(REF,E)), _shared_value(E,V).
evaluated(REF,bad) :- ch_post(evaluate(REF,E)), #false: _shared_value(E,V).
