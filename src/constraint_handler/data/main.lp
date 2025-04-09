% #include "direct.lp".
% #include "gringoEval.lp".
% #include "display.lp".

#defined requestEngine/2.
defaultEngine(compile).

requestedEngine(CNAME) :- requestEngine(CNAME,ENG).
engine(CNAME,ENG) :- requestEngine(CNAME,ENG).
engine(CNAME,ENG) :- defaultEngine(ENG), not requestedEngine(CNAME), ensure(CNAME,EXPR).
engine(CNAME,ENG) :- defaultEngine(ENG), not requestedEngine(CNAME), assign(CNAME,X,EXPR).
engine(CNAME,ENG) :- defaultEngine(ENG), not requestedEngine(CNAME), assignToSet(CNAME,X,EXPR).

value(X,T,V) :- eValue(variable(X),T,V).

representation((bool;int;str;float),extensional).
representation((intensionalSet),intensional).