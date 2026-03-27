#defined optimize_precision/1.
#defined optimize_precision/2.
#defined optimize_maximizeSum/3.
#defined optimize_maximizeSum/4.

optimize_maximizeSum(_label_anonymous,E,X,0) :- optimize_maximizeSum(E,X).
optimize_maximizeSum(_label_anonymous,E,X,P) :- optimize_maximizeSum(E,X,P).

engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), optimize_maximizeSum(CNAME,E,X,P).

% 4-parameter version with explicit priority
_optimize_maximizeSum(CNAME,E,X,P) :- optimize_maximizeSum(CNAME,E,X,P).

% Default precision for all priorities if not specified
_optimize_precision(PREC,P) :- optimize_precision(PREC), not optimize_precision(_,P), _optimize_maximizeSum(_,_,_,P).
% Precision for specific priority (priority is last argument)
_optimize_precision(PREC,P) :- optimize_precision(PREC,P).
% Default precision value of 1 if no precision is specified at all
_optimize_precision(val(int,1),P) :- _optimize_maximizeSum(_,_,_,P), not optimize_precision(_), not optimize_precision(_,P).

_optimize_se_maximizeSum(CNAME,E,X,P) :- _optimize_maximizeSum(CNAME,E,X,P), engine(CNAME,compile).

_optimize_se_component(operation(python("lambda v,p: math.floor(v*p)"),(E,(PREC,()))),X,P) :- _optimize_se_maximizeSum(CNAME,E,X,P),
  _optimize_precision(PREC,P).

direct_query(E) :- _optimize_se_component(E,X,P).

#maximize { I@P,X : _optimize_se_component(E,X,P), _se_value(E,val(int,I)) }.
