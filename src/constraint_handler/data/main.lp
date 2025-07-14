% #include "direct.lp".
% #include "gringoEval.lp".
% #include "display.lp".

#defined computed/4.
#defined requestEngine/2.
defaultEngine(compile).
%defaultEngine(ground).

requestedEngine(CNAME) :- requestEngine(CNAME,ENG).
engine(CNAME,ENG) :- requestEngine(CNAME,ENG).
engine(CNAME,ENG) :- defaultEngine(ENG), not requestedEngine(CNAME), ensure(CNAME,EXPR).
engine(CNAME,ENG) :- defaultEngine(ENG), not requestedEngine(CNAME), assign(CNAME,X,EXPR).
engine(CNAME,ENG) :- defaultEngine(ENG), not requestedEngine(CNAME), set_assign(CNAME,X,EXPR).
engine(CNAME,ENG) :- defaultEngine(ENG), not requestedEngine(CNAME), multimap_assign(CNAME,X,EKEY,EVAL).

value(X,T,V) :- eValue(variable(X),T,V).

representation((bool;int;str;float;symbol),extensional).
