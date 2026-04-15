% 4-parameter version with explicit priority
_optimize_maximizeSum(LBL,E,X,P) :- _passed(sugar,optimize_maximizeSum(LBL,E,X,P)).
_optimize_precision(PREC,PRIO) :- _passed(sugar,optimize_precision(PREC,PRIO)).

% Precision for specific priority (priority is last argument)
_passed(defaultArgs,optimize_precision(PREC,PRIO)) :- optimize_precision(PREC,PRIO).
% Default precision for all priorities if not specified
_passed(defaultArgs,optimize_precision(PREC,PRIO)) :- optimize_precision(PREC), not optimize_precision(_,PRIO), _optimize_maximizeSum(LBL,E,X,PRIO).
% Default precision value of 1 if no precision is specified at all
_passed(defaultArgs,optimize_precision(val(int,1),PRIO)) :- _optimize_maximizeSum(LBL,E,X,PRIO), not optimize_precision(_), not optimize_precision(_,PRIO).

_optimize_se_maximizeSum(CNAME,E,X,P) :- _optimize_maximizeSum(CNAME,E,X,P), engine(CNAME,compile).

_optimize_se_component(operation(python("lambda v,p: math.floor(v*p)"),(E,(PREC,()))),X,P) :- _optimize_se_maximizeSum(CNAME,E,X,P),
  _optimize_precision(PREC,P).

direct_query(E) :- _optimize_se_component(E,X,P).

#maximize { I@P,X : _optimize_se_component(E,X,P), _se_value(E,val(int,I)) }.
