_warning(variable(emptyDomain),(LBL,()),X) :- _passed(sugar,LBL,variable_declare(X,fromFacts)), #false: _passed(sugar,LBL2,variable_domain(X,E)).
