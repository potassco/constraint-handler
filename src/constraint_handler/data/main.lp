% #include "direct.lp".
% #include "4_solve/ground/gringoEval.lp".
% #include "display.lp".

#defined _computed/4.
#defined main_solverIdentifier/1.

_main_solverIdentifierAux(#inf,()).
_main_solverIdentifierAux(Y,(Y,L)) :- _main_solverIdentifierAux(X,L), main_solverIdentifier(Y), X < Y, 0 = #count { Z : main_solverIdentifier(Z), X < Z, Z < Y }.
_main_solverIdentifiers(L) :- _main_solverIdentifierAux(X,L), 0 = #count { Z : main_solverIdentifier(Z), X < Z }.


%%%%%%%%%%%%%%%%% parameters
#defined parameter_request/2.

_parameter(type_substituteBad).
_parameter_default(type_substituteBad,true).

_parameter_userRequest(PARAM) :- parameter_request(PARAM,BOOL), _parameter(PARAM).
_parameter_value(PARAM,VAL) :- _parameter_default(PARAM,VAL), not _parameter_userRequest(PARAM).
_parameter_value(PARAM,VAL) :- parameter_request(PARAM,VAL).

%%%%%%%%%%%%%%%%% version
version("0.0.4").