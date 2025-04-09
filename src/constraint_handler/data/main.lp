% #include "direct.lp".
% #include "gringoEval.lp".
% #include "display.lp".

#defined requestEngine/2.
defaultEngine(compile).

requestedEngine(CNAME) :- requestEngine(CNAME,ENG).
engine(CNAME,ENG) :- requestEngine(CNAME,ENG).
engine(CNAME,ENG) :- defaultEngine(ENG), not requestedEngine(CNAME), ensure(CNAME,EXPR).
engine(CNAME,ENG) :- defaultEngine(ENG), not requestedEngine(CNAME), assign(CNAME,VAR,EXPR).
engine(CNAME,ENG) :- defaultEngine(ENG), not requestedEngine(CNAME), assignToSet(CNAME,VAR,EXPR).
