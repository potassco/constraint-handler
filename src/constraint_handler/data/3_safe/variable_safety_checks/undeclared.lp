_warning(variable(undeclared),(),X) :- _variable(sugar,X), not _variable_exists(sugar,X).
_passed(correction(undeclared,add),_internal0,variable_declare(_internal0,X,definition)) :- _variable(sugar,X), not _variable_exists(sugar,X).
_passed(correction(undeclared,add),_internal0,variable_define(_internal0,X,bad)) :- _variable(sugar,X), not _variable_exists(sugar,X).

_variable_declared(X) :- _passed(defaultArgs,variable_declare(LBL,X,fromFacts)).
_passed(sugar,variable_declare(LBL,X,fromFacts)) :- _passed(defaultArgs,variable_domain(LBL,X,E)), not _variable_declared(X).
_warning(variable(undeclared),(),X) :- _passed(defaultArgs,variable_domain(LBL,X,E)), not _variable_declared(X).
