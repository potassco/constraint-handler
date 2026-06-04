_variable_hasDomain(sugar,X) :- _passed(sugar,variable_domain(LBL,X,E)).
_warning(variable(emptyDomain),(LBL,()),X) :- _passed(sugar,variable_declare(LBL,X,fromFacts)), not _variable_hasDomain(sugar,X).
