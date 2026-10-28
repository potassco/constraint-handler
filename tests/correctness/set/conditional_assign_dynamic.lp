variable_declare(x,fromFacts).
variable_domain(x,val(int,(1;2))).
variable_declare(s,set).
set_assign(s,variable(x),operation(eq,(variable(x),(val(int,2),())))).
