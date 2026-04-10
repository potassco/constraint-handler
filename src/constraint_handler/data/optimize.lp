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
