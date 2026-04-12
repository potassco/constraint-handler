propagator_ensure(CNAME,E) :- _passed(sugar,ensure(CNAME,E)), engine(CNAME,propagator).
propagator_assign(CNAME,X,E) :- assign(CNAME,X,E), engine(CNAME,propagator).
propagator_evaluate(CNAME,F,E) :- _passed(sugar,evaluate(CNAME,F,E)), engine(CNAME,propagator).

propagator_variable_declare(CNAME,X,E) :- _passed(sugar,variable_declare(CNAME,X,E)), engine(CNAME,propagator).
propagator_variable_domain(CNAME,X,D) :- _passed(sugar,variable_domain(CNAME,X,D)), engine(CNAME,propagator).
propagator_variable_define(CNAME,X,E) :- _passed(sugar,variable_define(CNAME,X,E)), engine(CNAME,propagator).

propagator_set_assign(CNAME,X,E) :- set_assign(CNAME,X,E), engine(CNAME,propagator).
propagator_set_baseDomain(CNAME,X,E) :- set_baseDomain(CNAME,X,E), engine(CNAME,propagator).
propagator_set_declare(CNAME,X) :- set_declare(CNAME,X), engine(CNAME,propagator).

propagator_multimap_assign(CNAME,X,K,V) :- multimap_assign(CNAME,X,K,V), engine(CNAME,propagator).
propagator_multimap_declare(CNAME,X) :- multimap_declare(CNAME,X), engine(CNAME,propagator).

propagator_optimize_maximizeSum(CNAME,E,X,P) :- _optimize_maximizeSum(CNAME,E,X,P), engine(CNAME,propagator).

propagator_execution_declare(CNAME,F,STMT,IN,OUT) :-
    execution_declare(CNAME,F,STMT,IN,OUT), engine(CNAME,propagator).

propagator_execution_run(CNAME,F) :-
    execution_run(CNAME,F), engine(CNAME,propagator).

propagator_forbid_warning(CNAME,W) :- forbid_warning(CNAME,W), defaultEngine(propagator).
