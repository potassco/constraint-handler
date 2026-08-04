_shared_value(E,V)    :- _optimize_component(LBL,E,ORIG,PREC,ID,P), _se_value(E,V).
_shared_value(ORIG,V) :- _optimize_component(LBL,E,ORIG,PREC,ID,P), _se_value(ORIG,V).
_shared_value(PREC,V) :- _optimize_component(LBL,E,ORIG,PREC,ID,P), _se_value(PREC,V).
#maximize { I@P,ID : _optimize_component(LBL,E,ORIG,PREC,ID,P), _se_value(E,val(int,I)) }.
