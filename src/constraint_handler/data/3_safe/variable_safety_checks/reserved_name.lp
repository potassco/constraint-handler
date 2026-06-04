_variable_reservedName(X) :- _variable_involve(defaultArgs,X,DECL), X=execution_output(PRG,Y).
_variable_reservedName(X) :- _variable_involve(defaultArgs,X,DECL), X=loc(_).

_passed(correction(reservedName,rem),DECL) :- _variable_reservedName(X), _variable_involve(sugar,X,DECL), _statement_introduce(LBL,X,E).
_passed(correction(reservedName,add),LBL,variable_declare(LBL,X,definition)) :- _variable_reservedName(X), _variable_involve(sugar,X,DECL), _statement_introduce(LBL,X,E).
_passed(correction(reservedName,add),LBL,variable_define(LBL,X,E)) :- _variable_reservedName(X), _variable_involve(sugar,X,DECL), _statement_introduce(LBL,X,E).

_warning(variable(reservedName),(),X) :- _variable_reservedName(X).
