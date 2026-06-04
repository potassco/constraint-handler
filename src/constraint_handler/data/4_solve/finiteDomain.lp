%%% rules for compile and ground engines

_variable_declare(compile,LBL,X) :- _passed(compile,LBL,variable_declare(X,fromFacts)).
_variable_declare(ground,LBL,X) :- _passed(ground,LBL,variable_declare(X,fromFacts)).
_variable_domain(X,E) :- _passed((compile;ground),LBL,variable_domain(X,E)).

_variable_hasDomain(X) :- _variable_domain(X,V).


%*
_variable_indexedDomain(X,E,IDX) :- _variable_domain(X,E), IDX=#count { F : _variable_domain(X,F), F < E }.
_passed(compile,LBL,variable_declare(LBL,X,definition)) :-
   _variable_declare(compile,LBL,X), _variable_hasDomain(X).
_passed(ground,LBL,variable_declare(LBL,X,definition)) :-
   _variable_declare(compile,LBL,X), _variable_hasDomain(X).
{ _variable_guess(X,IDX) } :-
   _variable_declare(compile,LBL,X), _variable_indexedDomain(X,E,IDX), IDX > 0.
{ _variable_guess(X,IDX) } :-
   _variable_declare(ground,LBL,X), _variable_indexedDomain(X,E,IDX), IDX > 0.
_variable_guess(X,0) :- _variable_hasDomain(X).
_variable_guess(X,IDX) :- _variable_guess(X,IDX+1), IDX > 0.
_passed(compile,LBL,variable_define(LBL,X,E)) :- _variable_declare(compile,LBL,X), _variable_guess(X,IDX), not _variable_guess(X,IDX+1), _variable_indexedDomain(X,E,IDX).
_passed(compile,LBL,ensure(LBL,operation(neq,(variable(X),(E,()))))) :- _variable_declare(compile,LBL,X), not _variable_guess(X,IDX), _variable_indexedDomain(X,E,IDX).
_passed(ground,LBL,variable_define(LBL,X,E)) :- _variable_declare(ground,LBL,X), _variable_guess(X,IDX), not _variable_guess(X,IDX+1), _variable_indexedDomain(X,E,IDX).
_passed(ground,LBL,ensure(LBL,operation(neq,(variable(X),(E,()))))) :- _variable_declare(ground,LBL,X), not _variable_guess(X,IDX), _variable_indexedDomain(X,E,IDX).
*%

direct_query(E) :- _variable_domain(X,E).
%direct_query(variable(X)) :- _variable_domain(X,E).
1 { _se_value(variable(X),V) : _variable_domain(X,E), _se_value(E,V) } 1 :-
   _variable_declare(compile,LBL,X), _variable_hasDomain(X), engine(LBL,compile).
1 { _ge_assign(LBL,X,V) : _variable_domain(X,E), _se_value(E,V) } 1 :-
   _variable_declare(ground,LBL,X), _variable_hasDomain(X), engine(LBL,ground).
