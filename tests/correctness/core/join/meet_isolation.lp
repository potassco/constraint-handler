variable_declare(join_enabled,boolDomain).
variable_declare(result,join,variable(join_enabled)).
variable_declare(result,meet,operation(lnot,(variable(join_enabled),()))).
variable_element(result,val(int,(1;4;7))).

bool_evaluate(operation(leqv,(variable(join_enabled),(operation(eq,(variable(result),(val(int,7),()))),())))).
