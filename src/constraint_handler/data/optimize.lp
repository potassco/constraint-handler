#defined optimize_precision/1.
#defined optimize_maximizeSum/3.
#defined optimize_maximizeSum/4.

engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), optimize_maximizeSum(CNAME,E,X).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), optimize_maximizeSum(CNAME,E,X,P).

% Support 3-parameter version with default priority 1
_optimize_maximizeSum(CNAME,E,X,1) :- engine(CNAME,compile), optimize_maximizeSum(CNAME,E,X).
% Support 4-parameter version with explicit priority
_optimize_maximizeSum(CNAME,E,X,P) :- engine(CNAME,compile), optimize_maximizeSum(CNAME,E,X,P).

_optimize_precision(PREC) :- optimize_precision(PREC).
_optimize_precision(val(int,1)) :- not optimize_precision(_).

optimize_component(ME,X,P) :- _optimize_maximizeSum(CNAME,E,X,P),
  _optimize_precision(PREC),
  ME = operation(CAST,(E,(PREC,()))),
  CAST = python("lambda v,p: math.floor(v*p)").

direct_query(E) :- optimize_component(E,X,P).

#maximize { I@P,X : optimize_component(E,X,P), _se_value(E,val(int,I)) }.
