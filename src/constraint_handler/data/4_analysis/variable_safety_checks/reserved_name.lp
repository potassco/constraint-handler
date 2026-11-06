_variable_name(reserved,X) :- _variable_involve(defaultArgs,LBL,X,DECL), X=execution_output(PRG,Y).
_variable_name(reserved,X) :- _variable_involve(defaultArgs,LBL,X,DECL), X=loc(_).
_variable_name(conflict,X) :- _variable_name(reserved,X), _statement_introduce(LBL,X,E).

_passed(correction(reservedName,rem),LBL,DECL) :- _variable_name(conflict,X), _variable_involve(sugar,LBL,X,DECL).
_passed(correction(reservedName,add),LBL,variable_declare(X,definition,C)) :- _variable_name(conflict,X), _passed(ssa,LBL,variable_declare(X,definition,C)).
_passed(correction(reservedName,add),LBL,variable_define(X,E,C)) :- _variable_name(conflict,X), _passed(ssa,LBL,variable_define(X,E,C)).

ch_core(warning_raise(variable(reservedName),X,val(bool,true)),LBL) :- _variable_name(reserved,X), _variable_involve(sugar,LBL,X,DECL).
