_variable_hasDomain(sugar,X) :- _passed(sugar,LBL,variable_domain(X,E)).
_warning(variable(emptyDomain),LBL,X) :- _passed(sugar,LBL,variable_declare(X,fromFacts)), not _variable_hasDomain(sugar,X).
_passed(correction(emptyDomain,rem),LBL,variable_declare(X,fromFacts)) :-
	_passed(sugar,LBL,variable_declare(X,fromFacts)),
	not _variable_hasDomain(sugar,X).
_passed(correction(emptyDomain,add),LBL,variable_declare(X,definition)) :-
	_passed(sugar,LBL,variable_declare(X,fromFacts)),
	not _variable_hasDomain(sugar,X).
_passed(correction(emptyDomain,add),LBL,variable_define(X,bad)) :-
	_passed(sugar,LBL,variable_declare(X,fromFacts)),
	not _variable_hasDomain(sugar,X).


_variable_hasSource(sugar,X) :- _passed(sugar,LBL,variable_assign(X,E)).
_variable_hasSource(sugar,X) :- _passed(sugar,LBL,variable_choice(X,E)).
_variable_hasSource(sugar,X) :- _passed(sugar,LBL,variable_default(X,E,C,P)).

_passed(correction(emptyDomain,rem),LBL,variable_assign(X,E)) :-
	_passed(sugar,LBL,variable_assign(X,E)),
	not _variable_hasSource(sugar,X).
_passed(correction(emptyDomain,rem),LBL,variable_choice(X,E)) :-
	_passed(sugar,LBL,variable_choice(X,E)),
	not _variable_hasSource(sugar,X).
_passed(correction(emptyDomain,rem),LBL,variable_default(X,E,C,P)) :-
	_passed(sugar,LBL,variable_default(X,E,C,P)),
	not _variable_hasSource(sugar,X).
_passed(correction(emptyDomain,rem),LBL,variable_declare(X,open)) :-
	_passed(sugar,LBL,variable_declare(X,open)),
	not _variable_hasSource(sugar,X).

_passed(correction(emptyDomain,add),LBL,variable_declare(X,definition)) :-
	_passed(sugar,LBL,variable_declare(X,open)),
	not _variable_hasSource(sugar,X).
_passed(correction(emptyDomain,add),LBL,variable_define(X,bad)) :-
	_passed(sugar,LBL,variable_declare(X,open)),
	not _variable_hasSource(sugar,X).
