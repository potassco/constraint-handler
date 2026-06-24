% #include "direct.lp".
% #include "4_solve/ground/gringoEval.lp".
% #include "display.lp".

#defined _computed/4.
#defined requestEngine/2.
#defined defaultEngine/1.
#defined main_solverIdentifier/1.

_main_solverIdentifierAux(#inf,()).
_main_solverIdentifierAux(Y,(Y,L)) :- _main_solverIdentifierAux(X,L), main_solverIdentifier(Y), X < Y, 0 = #count { Z : main_solverIdentifier(Z), X < Z, Z < Y }.
_main_solverIdentifiers(L) :- _main_solverIdentifierAux(X,L), 0 = #count { Z : main_solverIdentifier(Z), X < Z }.


% needed for brave reasoning?

representation((bool;int;string;float;symbol;none),extensional).

%%%%%%%%%%%%%%%%% warnings
_warning_forbid(KIND) :- _passed(sugar,LBL,warning_forbid(KIND)).
_warning_ignore(KIND) :- _passed(sugar,LBL,warning_ignore(KIND)).
:- _warning(KIND,INFO,MSG), _warning_forbid(KIND), not _warning_ignore(KIND).

%%%%%%%%%%%%%%%%% phases
#defined phase_request/2.

_phase(solve).
_phase_default(solve,true).
_phase(constantFolding).
_phase_default(constantFolding,true).
_phase(float_normalize).
_phase_default(float_normalize,true).
_phase(safe).
_phase_default(safe,true).
_phase(type_check).
_phase_default(type_check,true).
_phase(wf_check).
_phase_default(wf_check,true).

_phase_userRequest(PHASE) :- phase_request(PHASE,BOOL), _phase(PHASE).
_phase_active(PHASE) :- _phase_default(PHASE,true), not _phase_userRequest(PHASE).
_phase_active(PHASE) :- phase_request(PHASE,true).
