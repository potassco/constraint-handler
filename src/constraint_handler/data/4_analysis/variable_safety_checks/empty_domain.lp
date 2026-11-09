_variable_hasDomain(sugar,X) :- _passed(sugar,LBL,variable_domain(X,E,C)).
ch_core(warning_raise(variable(emptyDomain),X,C),LBL) :- _passed(sugar,LBL,variable_declare(X,fromFacts,C)), not _variable_hasDomain(sugar,X).
_passed(correction(emptyDomain,rem),LBL,variable_declare(X,fromFacts,C)) :-
	_passed(sugar,LBL,variable_declare(X,fromFacts,C)),
	not _variable_hasDomain(sugar,X).
_passed(correction(emptyDomain,add),LBL,variable_declare(X,definition,C)) :-
	_passed(sugar,LBL,variable_declare(X,fromFacts,C)),
	not _variable_hasDomain(sugar,X).
_passed(correction(emptyDomain,add),LBL,variable_define(X,bad,C)) :-
	_passed(sugar,LBL,variable_declare(X,fromFacts,C)),
	not _variable_hasDomain(sugar,X).


_variable_hasSource(sugar,X) :- _passed(sugar,LBL,variable_assign(X,E,C)).
_variable_hasSource(sugar,X) :- _passed(sugar,LBL,variable_choice(X,E,C)).
_variable_hasSource(sugar,X) :- _passed(sugar,LBL,variable_default(X,E,C,P)).

_passed(correction(emptyDomain,rem),LBL,variable_assign(X,E,C)) :-
	_passed(sugar,LBL,variable_assign(X,E,C)),
	not _variable_hasSource(sugar,X).
_passed(correction(emptyDomain,rem),LBL,variable_choice(X,E,C)) :-
	_passed(sugar,LBL,variable_choice(X,E,C)),
	not _variable_hasSource(sugar,X).
_passed(correction(emptyDomain,rem),LBL,variable_default(X,E,C,P)) :-
	_passed(sugar,LBL,variable_default(X,E,C,P)),
	not _variable_hasSource(sugar,X).
_passed(correction(emptyDomain,rem),LBL,variable_declare(X,open,C)) :-
	_passed(sugar,LBL,variable_declare(X,open,C)),
	not _variable_hasSource(sugar,X).

_passed(correction(emptyDomain,add),LBL,variable_declare(X,definition,C)) :-
	_passed(sugar,LBL,variable_declare(X,open,C)),
	not _variable_hasSource(sugar,X).
_passed(correction(emptyDomain,add),LBL,variable_define(X,bad,C)) :-
	_passed(sugar,LBL,variable_declare(X,open,C)),
	not _variable_hasSource(sugar,X).
