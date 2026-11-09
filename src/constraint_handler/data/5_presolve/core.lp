ch_solve(DECL,LBL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=bool_evaluate(E).
ch_solve(DECL,LBL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=variable_assign(X,E,C).
ch_solve(DECL,LBL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=variable_choice(X,E,C).
ch_solve(DECL,LBL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=variable_declare(X,D,C).

_bool_join(COND1,COND2) :- _phase_active(solve), ch_core(variable_default(NAME,EXPR,COND1,PRIORITY),_), ch_core(variable_declare(NAME,open,COND2),_).
_bool_join(COND1,COND2) :- _phase_active(solve), ch_core(variable_define(NAME,EXPR,COND1),_), ch_core(variable_declare(NAME,definition,COND2),_).
_bool_join(COND1,COND2) :- _phase_active(solve), ch_core(variable_domain(NAME,EXPR,COND1),_), ch_core(variable_declare(NAME,fromFacts,COND2),_).
_bool_join(COND1,COND2) :- _phase_active(solve), ch_core(set_assign(NAME,EXPR,COND1),_), ch_core(variable_declare(NAME,set,COND2),_).

_bool_joined(COND,COND,COND) :- _bool_join(COND,COND).
_bool_joined(COND,val(bool,true),COND) :- _bool_join(COND,val(bool,true)), COND != val(bool,true).
_bool_joined(val(bool,true),COND,COND) :- _bool_join(val(bool,true),COND), COND != val(bool,true).
_bool_joined(COND1,COND2,operation(conj,(COND2,(COND1,())))) :- _bool_join(COND1,COND2), COND1 != COND2, COND1 != val(bool,true), COND2 != val(bool,true).

ch_solve(variable_default(NAME,EXPR,JOINED,PRIORITY),LBL) :- _phase_active(solve), ch_core(variable_default(NAME,EXPR,COND1,PRIORITY),LBL), ch_core(variable_declare(NAME,open,COND2),_), _bool_joined(COND1,COND2,JOINED).
ch_solve(variable_define(NAME,EXPR,JOINED),LBL) :- _phase_active(solve), ch_core(variable_define(NAME,EXPR,COND1),LBL), ch_core(variable_declare(NAME,definition,COND2),_), _bool_joined(COND1,COND2,JOINED).
ch_solve(variable_domain(NAME,EXPR,JOINED),LBL) :- _phase_active(solve), ch_core(variable_domain(NAME,EXPR,COND1),LBL), ch_core(variable_declare(NAME,fromFacts,COND2),_), _bool_joined(COND1,COND2,JOINED).
ch_solve(set_assign(NAME,EXPR,JOINED),LBL) :- _phase_active(solve), ch_core(set_assign(NAME,EXPR,COND1),LBL), ch_core(variable_declare(NAME,set,COND2),_), _bool_joined(COND1,COND2,JOINED).

ch_solve(DECL,LBL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=multimap_assign(X,K,B,C).
ch_solve(DECL,LBL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=share_value(E).

%_passed(solve,LBL,share_value(E)) :- _phase_active(solve), ch_core(bool_evaluate(E),LBL).
%_passed(solve,LBL,share_value(E)) :- _phase_active(solve), ch_core(evaluate(REF,E),LBL).
%_passed(solve,LBL,share_value(E)) :- _phase_active(solve), ch_core(ensure(E),LBL).
%_passed(solve,LBL,share_value(E)) :- _phase_active(solve), ch_core(preference_holds(K,E),LBL).
%_passed(solve,LBL,DECL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=evaluate(REF,E).
