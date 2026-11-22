variable_declare(pool,set).
set_baseDomain(pool,val(int,1..3)).
ensure(operation(set_isin,(val(int,1),(variable(pool),())))).
ensure(operation(set_notin,(val(int,N),(variable(pool),())))) :- N=2..3.
variable_define(out,(val(string,"pool"),variable(pool))).
#show value/2.
