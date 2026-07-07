%%%%%%%%%%%%%%%%% bool_evaluate
1 { bool_evaluated(E,(bad;val(bool,(true;false)))) } 1 :- _passed(propagator,LBL,bool_evaluate(E)).
bool_evaluated(E,V) :- _passed((compile;compile3;ground),LBL,bool_evaluate(E)), _se_value(E,V), V=(bad;val(bool,(true;false))).
