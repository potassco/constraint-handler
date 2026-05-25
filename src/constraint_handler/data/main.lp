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


%%%%%%%%%%%%%%%%% engines
_main_engine(compile;ground;propagator;none).

_main_defaultEngine(ENG) :- defaultEngine(ENG), _main_engine(ENG).
_main_defaultEngineProvided :- defaultEngine(ENG), _main_engine(ENG).
_main_defaultEngine(compile) :- not _main_defaultEngineProvided.

_label(LBL) :- _label(LBL,DECL).
_main_requestedEngine(LBL) :- requestEngine(LBL,ENG), _main_engine(ENG).
engine(LBL,ENG) :- requestEngine(LBL,ENG), _main_engine(ENG).
engine(LBL,ENG) :- _main_defaultEngine(ENG), not _main_requestedEngine(LBL), _label(LBL).
engine(_internal,compile).
_passed(propagator,DECL) :- _label(LBL,DECL), engine(LBL,propagator).

% needed for brave reasoning?
value(X,V) :- _se_value(variable(X),V).

representation((bool;int;string;float;symbol;none),extensional).

_warning_forbid(KIND) :- _passed(wf_check,warning_forbid(LBL,KIND)).
_warning_ignore(KIND) :- _passed(wf_check,warning_ignore(LBL,KIND)).
:- _warning(KIND,INFO,MSG), _warning_forbid(KIND), not _warning_ignore(KIND).
warning(KIND,INFO,MSG) :- _warning(KIND,INFO,MSG), not _warning_ignore(KIND).
