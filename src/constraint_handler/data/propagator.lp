propagator_bool_evaluate(LBL,E) :- _passed(propagator,bool_evaluate(LBL,E)).
propagator_ensure(LBL,E) :- _passed(propagator,ensure(LBL,E)).
propagator_evaluate(LBL,O,E) :- _passed(propagator,evaluate(LBL,O,E)).


propagator_variable_declare(CNAME,X,fromFacts) :- _passed(propagator,variable_declare(CNAME,X,fromFacts)).

{propagator_variable_domain(CNAME,X, D) : _passed(propagator,variable_domain(CNAME,X,D))} 1 :- _passed(propagator,variable_declare(CNAME,X,fromFacts)).

order(CNAME,X,E,IDX) :- _passed(propagator,variable_domain(CNAME,X,E)), IDX = #count { E2 : _passed(propagator,variable_domain(CNAME,X,E2)), E2 < E }.

higher_assigned_domain(CNAME,X,D) :- _passed(propagator,variable_domain(CNAME,X,D)), propagator_variable_domain(CNAME,X,D2), order(CNAME,X,D,N-1), order(CNAME,X,D2,N).
higher_assigned_domain(CNAME,X,D) :- _passed(propagator,variable_domain(CNAME,X,D)), higher_assigned_domain(CNAME,X,D2), order(CNAME,X,D,N-1), order(CNAME,X,D2,N).

propagator_ensure(CNAME,operation(neq,(variable(V),(E1,())))) :- higher_assigned_domain(CNAME,V,E1), _passed(propagator,variable_domain(CNAME,V,E1)).


propagator_variable_define(CNAME,X,E) :- _passed(propagator,variable_define(CNAME,X,E)).

propagator_set_declare(CNAME,X) :- _passed(propagator,variable_declare(CNAME,X,set)).
propagator_set_assign(CNAME,X,E) :- _passed(propagator,set_assign(CNAME,X,E)).

{propagator_set_baseDomain(CNAME1,X,E) : _passed(propagator,set_baseDomain(CNAME1,X,E))} :- propagator_set_declare(CNAME2,X).

% ensure that value of expr is not in set if not chosen
propagator_ensure(CNAME,operation(set_notin,(E,(variable(X),())))) :- _passed(propagator,set_baseDomain(CNAME,X,E)), not propagator_set_baseDomain(CNAME,X,E).

propagator_multimap_assign(LBL,X,K,V) :- _passed(propagator,multimap_assign(LBL,X,K,V)).
propagator_multimap_declare(LBL,X) :- _passed(propagator,variable_declare(LBL,X,multimap)).

propagator_optimize_maximizeSum(LBL,E,X,P) :- _passed(propagator,optimize_maximizeSum(LBL,E,X,P)).
propagator_optimize_precision(PREC,PRIO) :- _passed(propagator,optimize_precision(LBL,PREC,PRIO)).

propagator_warning_forbid(LBL,W) :- _passed(solve,warning_forbid(LBL,W)).
propagator_warning_ignore(LBL,W) :- _passed(solve,warning_ignore(LBL,W)).
