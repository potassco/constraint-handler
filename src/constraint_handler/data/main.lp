% #include "direct.lp".
% #include "gringoEval.lp".
% #include "display.lp".

#defined _computed/4.
#defined requestEngine/2.
#defined defaultEngine/1.
#defined main_solverIdentifier/1.

_main_solverIdentifierAux(#inf,()).
_main_solverIdentifierAux(Y,(Y,L)) :- _main_solverIdentifierAux(X,L), main_solverIdentifier(Y), X < Y, 0 = #count { Z : main_solverIdentifier(Z), X < Z, Z < Y }.
_main_solverIdentifiers(L) :- _main_solverIdentifierAux(X,L), 0 = #count { Z : main_solverIdentifier(Z), X < Z }.


% needed for brave reasoning?
value(X,V) :- _se_value(variable(X),V).

representation((bool;int;string;float;symbol;none),extensional).

_warning_forbid(KIND) :- _passed(sugar,warning_forbid(LBL,KIND)).
_warning_ignore(KIND) :- _passed(sugar,warning_ignore(LBL,KIND)).
:- _warning(KIND,INFO,MSG), _warning_forbid(KIND), not _warning_ignore(KIND).
warning(KIND,INFO,MSG) :- _warning(KIND,INFO,MSG), not _warning_ignore(KIND).
