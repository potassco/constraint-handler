_expression(PHASE,LBL,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=bool_evaluate(E).
_expression(PHASE,LBL,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=ensure(E).
_expression(PHASE,LBL,DECL,operation(OP,ARGS)) :- _passed(PHASE,LBL,DECL), DECL=evaluate(OP,ARGS).

_expression(PHASE,LBL,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=variable_assign(X,E).
_expression(PHASE,LBL,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=variable_choice(X,E).
_expression(PHASE,LBL,DECL,(D;C)) :- _passed(PHASE,LBL,DECL), DECL=variable_default(X,D,C,P).
_expression(PHASE,LBL,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=variable_define(X,E).
_expression(PHASE,LBL,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=variable_domain(X,E).
_expression(PHASE,LBL,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=set_assign(X,E).
_expression(PHASE,LBL,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=set_baseDomain(X,E).
_expression(PHASE,LBL,DECL,(K;B)) :- _passed(PHASE,LBL,DECL), DECL=multimap_assign(X,K,B).
_expression(PHASE,LBL,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=share_value(E).
_expression(PHASE,LBL,DECL,(E;O;P)) :- _passed(PHASE,LBL,DECL), DECL=optimize_component(E,O,P,X,PRIORITY).
_expression(PHASE,LBL,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=preference_holds(E,K).

_expression(PHASE,E) :- _expression(PHASE,LBL,DECL,E).
_expression(PHASE,D) :- _expression(PHASE,operation(O,L)), D=@pythonListElements(L).
_expression(PHASE,D) :- _expression(PHASE,T), D=@pythonTupleElements(T).

_number(PHASE,LBL,DECL,PRIO) :- _passed(PHASE,LBL,DECL), DECL=variable_default(X,D,C,PRIO).
_number(PHASE,LBL,DECL,PRIO) :- _passed(PHASE,LBL,DECL), DECL=optimize_component(E,ORIG,PREC,X,PRIO).
_number(PHASE,LBL,DECL,K) :- _passed(PHASE,LBL,DECL), DECL=preference_holds(E,K).
_number(PHASE,K) :- _number(PHASE,LBL,DECL,K).

_variable(PHASE,X) :- _expression(PHASE,variable(X)).
_expression(PHASE,variable(X)) :- _passed(PHASE,LBL,variable_assign(X,E)).
_expression(PHASE,variable(X)) :- _passed(PHASE,LBL,variable_choice(X,E)).
_expression(PHASE,variable(X)) :- _passed(PHASE,LBL,variable_default(X,D,C,P)).
_expression(PHASE,variable(X)) :- _passed(PHASE,LBL,variable_define(X,E)).
_expression(PHASE,variable(X)) :- _passed(PHASE,LBL,variable_domain(X,E)).
_expression(PHASE,variable(X)) :- _passed(PHASE,LBL,set_assign(X,E)).
_expression(PHASE,variable(X)) :- _passed(PHASE,LBL,set_baseDomain(X,E)).
_expression(PHASE,variable(X)) :- _passed(PHASE,LBL,multimap_assign(X,K,B)).
