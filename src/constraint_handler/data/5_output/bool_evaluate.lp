%%%%%%%%%%%%%%%%% bool_evaluate
1 { bool_evaluated(E,(bad;val(bool,(true;false)))) } 1 :- _passed(propagator,bool_evaluate(LBL,E)).
bool_evaluated(E,V) :- _passed((compile;ground),bool_evaluate(LBL,E)), _se_value(E,V), V=(bad;val(bool,(true;false))).
