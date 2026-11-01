variable_declare(enabled,boolDomain).
variable_declare(active_facts,fromFacts,val(bool,true)).
variable_declare(disabled_facts,fromFacts,val(bool,false)).
variable_declare(dynamic_facts,fromFacts,variable(enabled)).
