% #include "direct.lp".
% #include "gringoEval.lp".
% #include "display.lp".

#defined computed/4.
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
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), ensure(CNAME,EXPR).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), assign(CNAME,X,EXPR).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), variable_declare(CNAME,X,EXPR).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), variable_define(CNAME,X,EXPR).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), set_assign(CNAME,X,EXPR).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), set_declare(CNAME,X).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), multimap_assign(CNAME,X,EKEY,EVAL).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), multimap_declare(CNAME,X).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), execution_declare(CNAME,FNAME,STMT,IN,OUT).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), execution_run(CNAME,FNAME).

value(X,val(T,V)) :- eValue(variable(X),T,V).

representation((bool;int;str;float;symbol;none),extensional).
