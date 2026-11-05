variable_declare(implicit,boolDomain).
variable_declare(enabled,boolDomain).
variable_declare(active,boolDomain,val(bool,true)).
variable_declare(disabled,boolDomain,val(bool,false)).
variable_declare(bad_condition,boolDomain,bad).
variable_declare(labeled,boolDomain,val(bool,true),named).
variable_declare(dynamic,boolDomain,variable(enabled)).

bool_evaluate(operation(conj,(operation(lnot,(variable(enabled),())),(variable(dynamic),())))).
bool_evaluate(variable(bad_condition)).
