propagator_bool_evaluate(LBL,E) :- _passed(propagator,LBL,bool_evaluate(E)).
propagator_ensure(LBL,E) :- _passed(propagator,LBL,ensure(E)).
propagator_evaluate(LBL,O,E) :- _passed(propagator,LBL,evaluate(O,E)).


propagator_variable_declare(CNAME,X,fromFacts) :- _passed(propagator,CNAME,variable_declare(X,fromFacts)).

1 {propagator_variable_domain(CNAME,X, D) : _passed(propagator,CNAME,variable_domain(X,D))} 1 :- _passed(propagator,CNAME,variable_declare(X,fromFacts)).

order(CNAME,X,E,IDX) :- _passed(propagator,CNAME,variable_domain(X,E)), IDX = #count { E2 : _passed(propagator,CNAME,variable_domain(X,E2)), E2 < E }.

higher_assigned_domain(CNAME,X,D) :- _passed(propagator,CNAME,variable_domain(X,D)), propagator_variable_domain(CNAME,X,D2), order(CNAME,X,D,N-1), order(CNAME,X,D2,N).
higher_assigned_domain(CNAME,X,D) :- _passed(propagator,CNAME,variable_domain(X,D)), higher_assigned_domain(CNAME,X,D2), order(CNAME,X,D,N-1), order(CNAME,X,D2,N).

propagator_ensure(CNAME,operation(neq,(variable(V),(E1,())))) :- higher_assigned_domain(CNAME,V,E1), _passed(propagator,CNAME,variable_domain(V,E1)).


propagator_variable_define(CNAME,X,E) :- _passed(propagator,CNAME,variable_define(X,E)).

propagator_set_declare(CNAME,X) :- _passed(propagator,CNAME,variable_declare(X,set)).
propagator_set_assign(CNAME,X,E) :- _passed(propagator,CNAME,set_assign(X,E)).

{propagator_set_baseDomain(CNAME1,X,E) : _passed(propagator,CNAME1,set_baseDomain(X,E))} :- propagator_set_declare(CNAME2,X).

% ensure that value of expr is not in set if not chosen
propagator_ensure(CNAME,operation(set_notin,(E,(variable(X),())))) :- _passed(propagator,CNAME,set_baseDomain(X,E)), not propagator_set_baseDomain(CNAME,X,E).

propagator_multimap_assign(LBL,X,K,V) :- _passed(propagator,LBL,multimap_assign(X,K,V)).
propagator_multimap_declare(LBL,X) :- _passed(propagator,LBL,variable_declare(X,multimap)).

propagator_optimize_maximizeSum(LBL,E,ID,PRIO) :- _passed(propagator,LBL,optimize_component(E,PREC,ID,PRIO)).
propagator_share_value(LBL,E) :- _passed(propagator,LBL,optimize_component(E,PREC,ID,PRIO)).
propagator_share_value(LBL,PREC) :- _passed(propagator,LBL,optimize_component(E,PREC,ID,PRIO)).

propagator_warning_forbid(LBL,W) :- _passed(solve,LBL,warning_forbid(W)).
propagator_warning_ignore(LBL,W) :- _passed(solve,LBL,warning_ignore(W)).


propagator_variable_interface(LBL,X) :- _passed(propagator,LBL,variable_interface(X)).
