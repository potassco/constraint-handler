_passed(solve,LBL,DECL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=bool_evaluate(E).
_passed(solve,LBL,DECL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=variable_assign(X,E).
_passed(solve,LBL,DECL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=variable_choice(X,E).
_passed(solve,LBL,DECL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=variable_declare(X,D).
_passed(solve,LBL,DECL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=variable_default(X,D,C,P).
_passed(solve,LBL,DECL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=variable_define(X,E).
_passed(solve,LBL,DECL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=variable_domain(X,E).
_passed(solve,LBL,DECL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=set_assign(X,E).
_passed(solve,LBL,DECL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=set_baseDomain(X,E).
_passed(solve,LBL,DECL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=multimap_assign(X,K,B).
_passed(solve,LBL,DECL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=share_value(E).
_passed(solve,LBL,DECL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=optimize_component(E,O,P,X,PRIORITY).

_variable_interface(X,LBL) :- ch_core(variable_declare(X,D),LBL), #false: X=loc(V).

_passed(solve,LBL,share_value(E)) :- _phase_active(solve), ch_core(bool_evaluate(E),LBL).
%_passed(solve,LBL,share_value(E)) :- _phase_active(solve), ch_core(evaluate(REF,E),LBL).
%_passed(solve,LBL,share_value(E)) :- _phase_active(solve), ch_core(ensure(E),LBL).
%_passed(solve,LBL,share_value(E)) :- _phase_active(solve), ch_core(preference_holds(E,K),LBL).
%_passed(solve,LBL,DECL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=evaluate(REF,E).
