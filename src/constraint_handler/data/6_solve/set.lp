%%%%%%%%%%%%%%%%% set_baseDomain
_set_baseDomain(X,E,LBL) :- _phase_active(solve), ch_core(set_baseDomain(X,E),LBL).

_passed(compile2,LBL,set_baseDomain(X,E)) :- _set_baseDomain(X,E,LBL), _engine(compile2,LBL).

_bool_evaluate(operation(set_isin,(E,(variable(X),()))),LBL) :- _set_baseDomain(X,E,LBL), _engine((compile;ground;propagator),LBL).
_passed(solve,LBL,variable_declare(loc(set_baseDomain(LBL,X,E)),fromFacts)) :- _set_baseDomain(X,E,LBL), _engine((compile;ground;propagator),LBL).
_passed(solve,LBL,variable_domain(loc(set_baseDomain(LBL,X,E)),val(bool,(false;true)))) :- _set_baseDomain(X,E,LBL), _engine((compile;ground;propagator),LBL).
_passed(solve,LBL,set_assign(X,E,variable(loc(set_baseDomain(LBL,X,E))))) :- _set_baseDomain(X,E,LBL), _engine((compile;ground;propagator),LBL).
_bool_evaluate(variable(loc(set_baseDomain(LBL,X,E))),LBL) :- _set_baseDomain(X,E,LBL), _engine((compile;ground;propagator),LBL).
:- _set_baseDomain(X,E,LBL), _engine((compile;ground;propagator),LBL),
   _bool_evaluated(operation(set_isin,(E,(variable(X),()))),val(bool,true)),
   not _bool_evaluated(variable(loc(set_baseDomain(LBL,X,E))),val(bool,true)).
