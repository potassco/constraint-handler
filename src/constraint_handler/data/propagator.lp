propagator_bool_evaluate(LBL,E) :- _passed(propagator,bool_evaluate(LBL,E)).
propagator_ensure(LBL,E) :- _passed(propagator,ensure(LBL,E)).
propagator_evaluate(LBL,O,E) :- _passed(propagator,evaluate(LBL,O,E)).


propagator_variable_declare(CNAME,X,E) :- _passed(propagator,variable_declare(CNAME,X,E)).

{propagator_variable_domain(CNAME,X, D) : _passed(propagator,variable_domain(CNAME,X,D))} 1 :- _passed(propagator,variable_declare(CNAME,X,_)).

order(CNAME,X,E,IDX) :- _passed(propagator,variable_domain(CNAME,X,E)), IDX = #count { E2 : _passed(propagator,variable_domain(CNAME,X,E2)), E2 < E }.

higher_assigned_domain(CNAME,X,D) :- _passed(propagator,variable_domain(CNAME,X,D)), propagator_variable_domain(CNAME,X,D2), order(CNAME,X,D,N-1), order(CNAME,X,D2,N).
higher_assigned_domain(CNAME,X,D) :- _passed(propagator,variable_domain(CNAME,X,D)), higher_assigned_domain(CNAME,X,D2), order(CNAME,X,D,N-1), order(CNAME,X,D2,N).

propagator_ensure(CNAME,operation(neq,(variable(V),(E1,())))) :- higher_assigned_domain(CNAME,V,E1), _passed(propagator,variable_domain(CNAME,V,E1)).


propagator_variable_define(CNAME,X,E) :- _passed(propagator,variable_define(CNAME,X,E)).

propagator_set_declare(CNAME,X) :- _passed(propagator,set_declare(CNAME,X)).
propagator_set_assign(CNAME,X,E) :- _passed(propagator,set_assign(CNAME,X,E)).

propagator_multimap_assign(LBL,X,K,V) :- _passed(propagator,multimap_assign(LBL,X,K,V)).
propagator_multimap_declare(LBL,X) :- _passed(propagator,multimap_declare(LBL,X)).

propagator_optimize_maximizeSum(LBL,E,X,P) :- _passed(propagator,optimize_maximizeSum(LBL,E,X,P)).
propagator_optimize_precision(PREC,PRIO) :- _passed(propagator,optimize_precision(LBL,PREC,PRIO)).

propagator_warning_forbid(LBL,W) :- _passed(ENG,warning_forbid(LBL,W)), _main_engine(ENG).
propagator_warning_ignore(LBL,W) :- _passed(ENG,warning_ignore(LBL,W)), _main_engine(ENG).
