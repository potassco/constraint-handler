propagator_ensure(CNAME,E) :- _passed(wf_check,ensure(CNAME,E)), engine(CNAME,propagator).
propagator_evaluate(CNAME,F,E) :- _passed(wf_check,evaluate(CNAME,F,E)), engine(CNAME,propagator).

propagator_bool_evaluate(LBL,E) :- _passed(wf_check,bool_evaluate(LBL,E)), engine(LBL,propagator).

propagator_variable_declare(CNAME,X,E) :- _passed(wf_check,variable_declare(CNAME,X,E)), engine(CNAME,propagator).

{propagator_variable_domain(CNAME,X, D) : _passed(wf_check,variable_domain(CNAME,X,D))} 1 :- _passed(wf_check,variable_declare(CNAME,X,_)), engine(CNAME,propagator).

order(CNAME,X,E,IDX) :- _passed(wf_check,variable_domain(CNAME,X,E)), IDX = #count { E2 : _passed(wf_check,variable_domain(CNAME,X,E2)), E2 < E }, engine(CNAME,propagator).

higher_assigned_domain(CNAME,X,D) :- _passed(wf_check,variable_domain(CNAME,X,D)), propagator_variable_domain(CNAME,X,D2), order(CNAME,X,D,N-1), order(CNAME,X,D2,N), engine(CNAME,propagator).
higher_assigned_domain(CNAME,X,D) :- _passed(wf_check,variable_domain(CNAME,X,D)), higher_assigned_domain(CNAME,X,D2), order(CNAME,X,D,N-1), order(CNAME,X,D2,N), engine(CNAME,propagator).

propagator_ensure(CNAME,operation(neq,(variable(V),(E1,())))) :- higher_assigned_domain(CNAME,V,E1), _passed(wf_check,variable_domain(CNAME,V,E1)), engine(CNAME,propagator).


propagator_variable_define(CNAME,X,E) :- _passed(wf_check,variable_define(CNAME,X,E)), engine(CNAME,propagator).

propagator_set_declare(CNAME,X) :- _passed(wf_check,set_declare(CNAME,X)), engine(CNAME,propagator).
propagator_set_assign(CNAME,X,E) :- _passed(wf_check,set_assign(CNAME,X,E)), engine(CNAME,propagator).

{propagator_set_baseDomain(CNAME1,X,E) : _passed(wf_check,set_baseDomain(CNAME1,X,E)), engine(CNAME1,propagator)} :- propagator_set_declare(CNAME2,X).

% ensure that value of expr is not in set if not chosen
propagator_ensure(CNAME,operation(set_notin,(E,(variable(X),())))) :- _passed(wf_check,set_baseDomain(CNAME,X,E)), not propagator_set_baseDomain(CNAME,X,E), engine(CNAME,propagator).


propagator_multimap_assign(LBL,X,K,V) :- _passed(wf_check,multimap_assign(LBL,X,K,V)), engine(LBL,propagator).
propagator_multimap_declare(LBL,X) :- _passed(wf_check,multimap_declare(LBL,X)), engine(LBL,propagator).

propagator_optimize_maximizeSum(LBL,E,X,P) :- _passed(wf_check,optimize_maximizeSum(LBL,E,X,P)), engine(LBL,propagator).
propagator_optimize_precision(PREC,PRIO) :- _passed(wf_check,optimize_precision(PREC,PRIO)).

propagator_warning_forbid(LBL,W) :- _passed(defaultArgs,warning_forbid(LBL,W)), defaultEngine(propagator).
propagator_warning_ignore(LBL,W) :- _passed(defaultArgs,warning_ignore(LBL,W)), defaultEngine(propagator).
