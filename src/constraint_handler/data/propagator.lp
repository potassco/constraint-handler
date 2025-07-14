propagator_ensure(CNAME,E) :- ensure(CNAME,E), engine(CNAME,propagator).
propagator_assign(CNAME,X,E) :- assign(CNAME,X,E), engine(CNAME,propagator).
