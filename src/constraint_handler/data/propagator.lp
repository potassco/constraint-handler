propagator_ensure(CNAME,E) :- _passed(wf_check,ensure(CNAME,E)), engine(CNAME,propagator).
propagator_assign(CNAME,X,E) :- assign(CNAME,X,E), engine(CNAME,propagator).
propagator_evaluate(CNAME,F,E) :- _passed(wf_check,evaluate(CNAME,F,E)), engine(CNAME,propagator).

propagator_bool_evaluate(LBL,E) :- _passed(wf_check,bool_evaluate(LBL,E)), engine(LBL,propagator).

propagator_variable_declare(CNAME,X,E) :- _passed(wf_check,variable_declare(CNAME,X,E)), engine(CNAME,propagator).
propagator_variable_domain(CNAME,X,D) :- _passed(wf_check,variable_domain(CNAME,X,D)), engine(CNAME,propagator).
propagator_variable_define(CNAME,X,E) :- _passed(wf_check,variable_define(CNAME,X,E)), engine(CNAME,propagator).

propagator_set_assign(CNAME,X,E) :- _passed(wf_check,set_assign(CNAME,X,E)), engine(CNAME,propagator).
propagator_set_baseDomain(CNAME,X,E) :- _passed(wf_check,set_baseDomain(CNAME,X,E)), engine(CNAME,propagator).
propagator_set_declare(CNAME,X) :- _passed(wf_check,set_declare(CNAME,X)), engine(CNAME,propagator).

propagator_multimap_assign(LBL,X,K,V) :- _passed(wf_check,multimap_assign(LBL,X,K,V)), engine(LBL,propagator).
propagator_multimap_declare(LBL,X) :- _passed(wf_check,multimap_declare(LBL,X)), engine(LBL,propagator).

propagator_optimize_maximizeSum(LBL,E,X,P) :- _passed(wf_check,optimize_maximizeSum(LBL,E,X,P)), engine(LBL,propagator).
propagator_optimize_precision(PREC,PRIO) :- _passed(wf_check,optimize_precision(PREC,PRIO)).

%propagator_execution_declare(LBL,F,STMT,IN,OUT) :-
%    _passed(wf_check,execution_declare(LBL,F,STMT,IN,OUT)), engine(LBL,propagator).

%propagator_execution_run(LBL,F) :-
%    _passed(wf_check,execution_run(LBL,F)), engine(LBL,propagator).

propagator_warning_forbid(LBL,W) :- warning_forbid(LBL,W), defaultEngine(propagator).
propagator_warning_ignore(LBL,W) :- warning_ignore(LBL,W), defaultEngine(propagator).
