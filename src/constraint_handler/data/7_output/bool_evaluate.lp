%%%%%%%%%%%%%%%%% bool_evaluate
1 { bool_evaluated(E,(bad;val(bool,(true;false)))) } :- _passed(propagator,LBL,bool_evaluate(E)).
bool_evaluated(E,V) :- _passed((compile;compile2;ground),LBL,bool_evaluate(E)), _se_value(E,V), V=(bad;val(bool,(true;false))).

:- _engine(ENG), _passed(ENG,LBL,bool_evaluate(E)), bool_evaluated(E,V0), bool_evaluated(E,V1), V0 < V1, V0=(bad;val(bool,(true;false))), V1=(bad;val(bool,(true;false))).

:- _engine(ENG), _passed(ENG,LBL,bool_evaluate(E)), bool_evaluated(E,V), V!=bad, V!=val(bool,true), V!=val(bool,false).
