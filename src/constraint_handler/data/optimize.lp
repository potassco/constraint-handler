#defined optimize_precision/1.
#defined optimize_precision/2.
#defined optimize_maximizeSum/3.
#defined optimize_maximizeSum/4.

engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), optimize_maximizeSum(CNAME,E,X).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), optimize_maximizeSum(CNAME,E,X,P).

% Map 3-parameter version to 4-parameter version with priority 0
_optimize_maximizeSum(CNAME,E,X,0) :- optimize_maximizeSum(CNAME,E,X).
% 4-parameter version with explicit priority
_optimize_maximizeSum(CNAME,E,X,P) :- optimize_maximizeSum(CNAME,E,X,P).

% Default precision for all priorities if not specified
_optimize_precision(PREC,P) :- optimize_precision(PREC), not optimize_precision(_,P), _optimize_maximizeSum(_,_,_,P).
% Precision for specific priority (priority is last argument)
_optimize_precision(PREC,P) :- optimize_precision(PREC,P).
% Default precision value of 1 if no precision is specified at all
_optimize_precision(val(int,1),P) :- _optimize_maximizeSum(_,_,_,P), not optimize_precision(_), not optimize_precision(_,P).

_optimize_se_maximizeSum(CNAME,E,X,P) :- _optimize_maximizeSum(CNAME,E,X,P), engine(CNAME,compile).

_optimize_se_component(ME,X,P) :- _optimize_se_maximizeSum(CNAME,E,X,P),
  _optimize_precision(PREC,P),
  ME = operation(CAST,(E,(PREC,()))),
  CAST = python("lambda v,p: math.floor(v*p)").

direct_query(E) :- _optimize_se_component(E,X,P).

#maximize { I@P,X : _optimize_se_component(E,X,P), _se_value(E,val(int,I)) }.
