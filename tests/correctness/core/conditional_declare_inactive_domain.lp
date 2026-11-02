variable_define(enabled,val(bool,true)).
variable_declare(empty,fromFacts,variable(enabled)).
variable_domain(empty,val(int,1),operation(lnot,(variable(enabled),()))).
