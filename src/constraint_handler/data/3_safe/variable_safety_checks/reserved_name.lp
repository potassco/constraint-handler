_variable_name(reserved,X) :- _variable_involve(defaultArgs,X,DECL), X=execution_output(PRG,Y).
_variable_name(reserved,X) :- _variable_involve(defaultArgs,X,DECL), X=loc(_).
_variable_name(conflict,X) :- _variable_name(reserved,X), _statement_introduce(LBL,X,E).

_passed(correction(reservedName,rem),LBL,DECL) :- _variable_name(conflict,X), _passed(sugar,LBL,DECL), DECL=variable_declare(X,D).
_passed(correction(reservedName,rem),LBL,DECL) :- _variable_name(conflict,X), _passed(sugar,LBL,DECL), DECL=variable_define(X,D).
_passed(correction(reservedName,rem),LBL,DECL) :- _variable_name(conflict,X), _passed(sugar,LBL,DECL), DECL=variable_domain(X,D).
_passed(correction(reservedName,rem),LBL,DECL) :- _variable_name(conflict,X), _passed(sugar,LBL,DECL), DECL=set_assign(X,D).
_passed(correction(reservedName,rem),LBL,DECL) :- _variable_name(conflict,X), _passed(sugar,LBL,DECL), DECL=set_baseDomain(X,D).
_passed(correction(reservedName,rem),LBL,DECL) :- _variable_name(conflict,X), _passed(sugar,LBL,DECL), DECL=multimap_assign(X,D,E2).
_passed(correction(reservedName,add),LBL,variable_declare(X,definition)) :- _variable_name(conflict,X), _statement_introduce(LBL,X,E).
_passed(correction(reservedName,add),LBL,variable_define(X,E)) :- _variable_name(conflict,X), _statement_introduce(LBL,X,E).

_warning(variable(reservedName),(),X) :- _variable_name(reserved,X).
