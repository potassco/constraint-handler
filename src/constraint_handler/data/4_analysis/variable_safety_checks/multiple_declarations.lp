% TODO: Check conflicting active declarations and emit warnings.

_variable_multipleAssignments(LBL1,X,D1) :-
  _passed(defaultArgs,LBL1,variable_assign(X,D1)),
  1 = #count { LBL0,D0 : _passed(defaultArgs,LBL0,variable_assign(X,D0)), (LBL0,D0) < (LBL1,D1) }.

_variable_multiple(LBL,X) :- _variable_multipleAssignments(LBL,X,D).
_passed(correction(multipleDeclarations,rem),LBL,DECL) :- _variable_multiple(LBL,X), _passed(sugar,LBL,DECL), DECL=variable_declare(X,D,C).
_passed(correction(multipleDeclarations,rem),LBL,DECL) :- _variable_multiple(LBL,X), _passed(sugar,LBL,DECL), DECL=variable_assign(X,D).
_passed(correction(multipleDeclarations,rem),LBL,DECL) :- _variable_multiple(LBL,X), _passed(sugar,LBL,DECL), DECL=variable_choice(X,D).
_passed(correction(multipleDeclarations,rem),LBL,DECL) :- _variable_multiple(LBL,X), _passed(sugar,LBL,DECL), DECL=variable_default(X,D,C,P).
_passed(correction(multipleDeclarations,rem),LBL,DECL) :- _variable_multiple(LBL,X), _passed(sugar,LBL,DECL), DECL=variable_define(X,D,C).
_passed(correction(multipleDeclarations,rem),LBL,DECL) :- _variable_multiple(LBL,X), _passed(sugar,LBL,DECL), DECL=variable_domain(X,D,C).
_passed(correction(multipleDeclarations,rem),LBL,DECL) :- _variable_multiple(LBL,X), _passed(sugar,LBL,DECL), DECL=set_assign(X,D,C).
_passed(correction(multipleDeclarations,rem),LBL,DECL) :- _variable_multiple(LBL,X), _passed(sugar,LBL,DECL), DECL=set_baseDomain(X,D,C).
_passed(correction(multipleDeclarations,rem),LBL,DECL) :- _variable_multiple(LBL,X), _passed(sugar,LBL,DECL), DECL=multimap_assign(X,D,E).
_passed(correction(multipleDeclarations,add),LBL,variable_declare(X,definition,val(bool,true))) :- _variable_multiple(LBL,X).
_passed(correction(multipleDeclarations,add),LBL,variable_define(X,bad,val(bool,true))) :- _variable_multiple(LBL,X).

ch_core(warning_raise(variable(multipleAssignments),(X,E0,E1),val(bool,true)),(LBL0;LBL1)) :-
  _variable_multipleAssignments(LBL1,X,E1),
  _passed(defaultArgs,LBL0,variable_assign(X,E0)), (LBL0,E0) < (LBL1,E1).
