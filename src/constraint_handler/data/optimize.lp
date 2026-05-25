_optimize_maximizeSum(LBL,E,X,P) :- _passed(solve,optimize_maximizeSum(LBL,E,X,P)), engine(LBL,compile).
_optimize_precision(PREC,PRIO) :- _passed(solve,optimize_precision(LBL,PREC,PRIO)).

_optimize_se_component(operation(floor,(operation(mult,(E,(PREC,()))),())),X,P) :- _optimize_maximizeSum(LBL,E,X,P),
  _optimize_precision(PREC,P), not type_expression(type_check,E,bool).
_optimize_se_component(operation(floor,(operation(mult,(operation(ite,(E,(val(int,1),(val(int,0),())))),(PREC,()))),())),X,P) :- _optimize_maximizeSum(LBL,E,X,P),
  _optimize_precision(PREC,P), type_expression(type_check,E,bool).

direct_query(E) :- _optimize_se_component(E,X,P).

#maximize { I@P,X : _optimize_se_component(E,X,P), _se_value(E,val(int,I)) }.
