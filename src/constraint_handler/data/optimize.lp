% 4-parameter version with explicit priority
% Precision for specific priority (priority is last argument)
_passed(defaultArgs,optimize_precision(PREC,PRIO)) :- optimize_precision(PREC,PRIO).
% Default precision for all priorities if not specified
_passed(defaultArgs,optimize_precision(PREC,PRIO)) :- optimize_precision(PREC), not optimize_precision(_,PRIO), _passed(sugar,optimize_maximizeSum(LBL,E,X,PRIO)).
% Default precision value of 1 if no precision is specified at all
_passed(defaultArgs,optimize_precision(val(int,1),PRIO)) :- _passed(sugar,optimize_maximizeSum(LBL,E,X,PRIO)), not optimize_precision(_), not optimize_precision(_,PRIO).

_optimize_maximizeSum(LBL,E,X,P) :- _passed(sugar,optimize_maximizeSum(LBL,E,X,P)), engine(LBL,compile).
_optimize_precision(PREC,PRIO) :- _passed(sugar,optimize_precision(PREC,PRIO)).

_optimize_se_component(operation(floor,(operation(mult,(E,(PREC,()))),())),X,P) :- _optimize_maximizeSum(LBL,E,X,P),
  _optimize_precision(PREC,P), not type_expression((),E,bool).
_optimize_se_component(operation(floor,(operation(mult,(operation(ite,(E,(val(int,1),(val(int,0),())))),(PREC,()))),())),X,P) :- _optimize_maximizeSum(LBL,E,X,P),
  _optimize_precision(PREC,P), type_expression((),E,bool).

direct_query(E) :- _optimize_se_component(E,X,P).

#maximize { I@P,X : _optimize_se_component(E,X,P), _se_value(E,val(int,I)) }.
