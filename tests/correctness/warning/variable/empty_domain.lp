variable_declare(enabled,boolDomain).
variable_declare(active_facts,fromFacts,variable(enabled),active).
variable_declare(inactive_facts,fromFacts,operation(lnot,(variable(enabled),())),inactive).

ensure(variable(enabled)).
