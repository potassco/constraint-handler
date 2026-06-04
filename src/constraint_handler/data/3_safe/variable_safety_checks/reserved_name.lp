_variable_reservedName(X) :- _variable_involve(defaultArgs,X,DECL), X=execution_output(PRG,Y).
_variable_reservedName(X) :- _variable_involve(defaultArgs,X,DECL), X=loc(_).

_passed(correction(reservedName,rem),LBL,DECL) :- _variable_reservedName(X), _passed(sugar,LBL,DECL), DECL=variable_declare(X,D), _statement_introduce(LBL,X,E).
_passed(correction(reservedName,rem),LBL,DECL) :- _variable_reservedName(X), _passed(sugar,LBL,DECL), DECL=variable_define(X,D), _statement_introduce(LBL,X,E).
_passed(correction(reservedName,rem),LBL,DECL) :- _variable_reservedName(X), _passed(sugar,LBL,DECL), DECL=variable_domain(X,D), _statement_introduce(LBL,X,E).
_passed(correction(reservedName,rem),LBL,DECL) :- _variable_reservedName(X), _passed(sugar,LBL,DECL), DECL=set_assign(X,D), _statement_introduce(LBL,X,E).
_passed(correction(reservedName,rem),LBL,DECL) :- _variable_reservedName(X), _passed(sugar,LBL,DECL), DECL=set_baseDomain(X,D), _statement_introduce(LBL,X,E).
_passed(correction(reservedName,rem),LBL,DECL) :- _variable_reservedName(X), _passed(sugar,LBL,DECL), DECL=multimap_assign(X,D,E2), _statement_introduce(LBL,X,E).
_passed(correction(reservedName,add),LBL,variable_declare(X,definition)) :- _variable_reservedName(X), _statement_introduce(LBL,X,E).
_passed(correction(reservedName,add),LBL,variable_define(X,E)) :- _variable_reservedName(X), _statement_introduce(LBL,X,E).

_warning(variable(reservedName),(),X) :- _variable_reservedName(X).
