ch_solve(DECL,LBL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=bool_evaluate(E).
ch_solve(DECL,LBL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=variable_assign(X,E).
ch_solve(DECL,LBL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=variable_choice(X,E).
ch_solve(DECL,LBL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=variable_declare(X,D).
ch_solve(DECL,LBL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=variable_default(X,D,C,P).
ch_solve(DECL,LBL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=variable_define(X,E).
ch_solve(DECL,LBL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=variable_domain(X,E).
ch_solve(DECL,LBL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=set_assign(X,E,C).
ch_solve(DECL,LBL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=multimap_assign(X,K,B).
ch_solve(DECL,LBL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=share_value(E).
ch_solve(DECL,LBL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=optimize_component(E,O,P,X,PRIORITY).

_variable_interface(X,LBL) :- ch_core(variable_declare(X,D),LBL), #false: X=loc(V).

%_passed(solve,LBL,share_value(E)) :- _phase_active(solve), ch_core(bool_evaluate(E),LBL).
%_passed(solve,LBL,share_value(E)) :- _phase_active(solve), ch_core(evaluate(REF,E),LBL).
%_passed(solve,LBL,share_value(E)) :- _phase_active(solve), ch_core(ensure(E),LBL).
%_passed(solve,LBL,share_value(E)) :- _phase_active(solve), ch_core(preference_holds(E,K),LBL).
%_passed(solve,LBL,DECL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=evaluate(REF,E).
