% #include "direct.lp".
% #include "gringoEval.lp".
% #include "display.lp".

#defined _computed/4.
#defined requestEngine/2.
#defined defaultEngine/1.
#defined main_solverIdentifier/1.

%%%%%%%%%%%%%%%%% engines
%%% compile
%%% ground
%%% propagator
%%% none

_main_solverIdentifier(X) :- main_solverIdentifier(X).
_main_solverIdentifier(none) :- not main_solverIdentifier(_).

_main_defaultEngine(ENG) :- defaultEngine(ENG).
_main_defaultEngine(compile) :- not defaultEngine(_).

requestedEngine(CNAME) :- requestEngine(CNAME,ENG).
engine(CNAME,ENG) :- requestEngine(CNAME,ENG).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), _label(CNAME).

value(X,V) :- _se_value(variable(X),V).

representation((bool;int;string;float;symbol;none),extensional).

:- _warning(KIND,INFO,MSG), forbid_warning(NAME,KIND), not ignore_warning(KIND).
warning(KIND,INFO,MSG) :- _warning(KIND,INFO,MSG), not ignore_warning(KIND).
