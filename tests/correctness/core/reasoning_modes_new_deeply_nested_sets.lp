variable_declare(value,set).
set_baseDomain(value,operation(set_make,(operation(set_make,(val(int,1..3),())),()))).
ensure(operation(eq,(operation(cardinality,(variable(value),())),(val(int,1),())))).
