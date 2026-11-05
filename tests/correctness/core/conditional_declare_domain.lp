variable_declare(enabled,boolDomain).
variable_declare(active_domain,fromFacts,val(bool,true)).
variable_declare(disabled_domain,fromFacts,val(bool,false)).
variable_declare(dynamic_domain,fromFacts,variable(enabled)).
variable_domain(active_domain,val(int,1)).
variable_domain(disabled_domain,val(int,1)).
variable_domain(dynamic_domain,val(int,1)).
