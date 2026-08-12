%%% rules for compile and ground engines

_finiteDomain_variable(compile,X) :- _passed(compile,LBL,variable_declare(X,fromFacts)).
_finiteDomain_variable(ground,X) :- _passed(ground,LBL,variable_declare(X,fromFacts)).
_finiteDomain_element(X,E) :- _passed((compile;ground),LBL,variable_domain(X,E)).

%_variable_hasDomain(X) :- _finiteDomain_element(X,V).


%*
_variable_guess(X,0) :- _variable_hasDomain(X).
_variable_guess(X,IDX) :- _variable_guess(X,IDX+1), IDX > 0.

_variable_indexedDomain(X,E,IDX) :- _finiteDomain_element(X,E), IDX=#count { F : _finiteDomain_element(X,F), F < E }.
_passed(compile,LBL,variable_declare(X,definition)) :-
   _finiteDomain_variable(compile,LBL,X), _variable_hasDomain(X).
{ _variable_guess(X,IDX) } :-
   _finiteDomain_variable(compile,LBL,X), _variable_indexedDomain(X,E,IDX), IDX > 0.
_passed(compile,LBL,variable_define(X,E)) :- _finiteDomain_variable(compile,LBL,X), _variable_guess(X,IDX), not _variable_guess(X,IDX+1), _variable_indexedDomain(X,E,IDX).
_passed(compile,LBL,ensure(operation(neq,(variable(X),(E,()))))) :- _finiteDomain_variable(compile,LBL,X), not _variable_guess(X,IDX), _variable_indexedDomain(X,E,IDX).

_passed(ground,LBL,variable_declare(X,definition)) :-
   _finiteDomain_variable(ground,LBL,X), _variable_hasDomain(X).
{ _variable_guess(X,IDX) } :-
   _finiteDomain_variable(ground,LBL,X), _variable_indexedDomain(X,E,IDX), IDX > 0.
_passed(ground,LBL,variable_define(X,E)) :- _finiteDomain_variable(ground,LBL,X), _variable_guess(X,IDX), not _variable_guess(X,IDX+1), _variable_indexedDomain(X,E,IDX).
_passed(ground,LBL,ensure(operation(neq,(variable(X),(E,()))))) :- _finiteDomain_variable(ground,LBL,X), not _variable_guess(X,IDX), _variable_indexedDomain(X,E,IDX).
*%

direct_query(E) :- _finiteDomain_element(X,E).
%direct_query(variable(X)) :- _finiteDomain_element(X,E).
1 { _se_value(variable(X),V) : _finiteDomain_element(X,E), _se_value(E,V) } 1 :-
   _finiteDomain_variable(compile,X).
1 { _ge_assign(X,V) : _finiteDomain_element(X,E), _se_value(E,V) } 1 :-
   _finiteDomain_variable(ground,X).
