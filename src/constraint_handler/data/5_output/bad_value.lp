_warning(variable(badValue),LBL,X) :- _se_value(variable(X),bad), not _variable_internal(X), _passed(sugar,LBL,variable_declare(X,D)).
