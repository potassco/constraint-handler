_warning(variable(undeclared),(),X) :- _variable(sugar,X), not _variable_exists(sugar,X).
_passed(correction(undeclared,add),_internal0,variable_declare(X,definition)) :- _variable(sugar,X), not _variable_exists(sugar,X).
_passed(correction(undeclared,add),_internal0,variable_define(X,bad)) :- _variable(sugar,X), not _variable_exists(sugar,X).

_variable_declared(X) :- _passed(defaultArgs,LBL,variable_declare(X,fromFacts)).
_passed(sugar,LBL,variable_declare(X,fromFacts)) :- _passed(defaultArgs,LBL,variable_domain(X,E)), not _variable_declared(X).
_warning(variable(undeclared),(),X) :- _passed(defaultArgs,LBL,variable_domain(X,E)), not _variable_declared(X).

_set_declared(X) :- _passed(defaultArgs,LBL,set_declare(X)).
_passed(sugar,LBL,variable_declare(X,set)) :- _passed(defaultArgs,LBL,set_baseDomain(X,E)), not _set_declared(X).
_passed(sugar,LBL,variable_declare(X,set)) :- _passed(defaultArgs,LBL,set_assign(X,E)), not _set_declared(X).
_warning(variable(undeclared),(),X) :- _passed(defaultArgs,LBL,set_baseDomain(X,E)), not _set_declared(X).
_warning(variable(undeclared),(),X) :- _passed(defaultArgs,LBL,set_assign(X,E)), not _set_declared(X).
