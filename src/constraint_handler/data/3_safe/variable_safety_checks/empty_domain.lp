_variable_hasDomain(sugar,X) :- _passed(sugar,LBL,variable_domain(X,E)).
_warning(variable(emptyDomain),(LBL,()),X) :- _passed(sugar,LBL,variable_declare(X,fromFacts)), not _variable_hasDomain(sugar,X).
_passed(correction(emptyDomain,rem),LBL,variable_declare(X,fromFacts)) :-
	_passed(sugar,LBL,variable_declare(X,fromFacts)),
	not _variable_hasDomain(sugar,X).
_passed(correction(emptyDomain,add),LBL,variable_declare(X,definition)) :-
	_passed(sugar,LBL,variable_declare(X,fromFacts)),
	not _variable_hasDomain(sugar,X).
_passed(correction(emptyDomain,add),LBL,variable_define(X,bad)) :-
	_passed(sugar,LBL,variable_declare(X,fromFacts)),
	not _variable_hasDomain(sugar,X).
