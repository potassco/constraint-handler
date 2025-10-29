propagator_ensure(CNAME,E) :- ensure(CNAME,E), engine(CNAME,propagator).
propagator_assign(CNAME,X,E) :- assign(CNAME,X,E), engine(CNAME,propagator).

propagator_set_assign(CNAME,X,E) :- set_assign(CNAME,X,E), engine(CNAME,propagator).
propagator_set_declare(CNAME,X) :- set_declare(CNAME,X), engine(CNAME,propagator).

propagator_multimap_assign(CNAME,X,K,V) :- multimap_assign(CNAME,X,K,V), engine(CNAME,propagator).
propagator_multimap_declare(CNAME,X) :- multimap_declare(CNAME,X), engine(CNAME,propagator).

