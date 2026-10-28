%%%%%%%%%%%%%%%%% set_baseDomain
_set_baseDomain(X,E,C,LBL,loc(set_baseDomain(LBL,X,E,C))) :- _phase_active(solve), ch_core(set_baseDomain(X,E,C),LBL).

_bool_evaluate(C,LBL) :- _set_baseDomain(X,E,C,LBL,Choice).
_bool_evaluate(operation(set_isin,(E,(variable(X),()))),LBL) :- _set_baseDomain(X,E,C,LBL,Choice).
ch_solve(variable_declare(Choice,fromFacts,val(bool,true)),LBL) :- _set_baseDomain(X,E,C,LBL,Choice).
ch_solve(variable_domain(Choice,val(bool,false),val(bool,true)),LBL) :- _set_baseDomain(X,E,C,LBL,Choice).
ch_solve(variable_domain(Choice,val(bool,true),C),LBL) :- _set_baseDomain(X,E,C,LBL,Choice).
ch_solve(set_assign(X,E,variable(Choice)),LBL) :- _set_baseDomain(X,E,C,LBL,Choice).
_bool_evaluate(variable(Choice),LBL) :- _set_baseDomain(X,E,C,LBL,Choice).
:- _set_baseDomain(X,E,C,LBL,Choice),
   _bool_evaluated(C,val(bool,true)),
   _bool_evaluated(operation(set_isin,(E,(variable(X),()))),val(bool,true)),
   not _bool_evaluated(variable(Choice),val(bool,true)).
