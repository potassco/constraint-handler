variable_declare(s,set).
set_baseDomain(s,s,val(int,(1..4))).

ensure(operation(set_isin,(val(int,1),(variable(s),())))).
ensure(operation(set_notin,(val(int,4),(variable(s),())))).
