_variable_multipleDeclarations(LBL1,X,D1) :-
  _passed(defaultArgs,LBL1,variable_declare(X,D1)),
  1 = #count { LBL0,D0 : _passed(defaultArgs,LBL0,variable_declare(X,D0)), (LBL0,D0) < (LBL1,D1) }.

_variable_multipleDefinitions(LBL1,X,D1) :-
  _passed(defaultArgs,LBL1,variable_define(X,D1)),
  1 = #count { LBL0,D0 : _passed(defaultArgs,LBL0,variable_define(X,D0)), (LBL0,D0) < (LBL1,D1) }.

_variable_multiple(LBL,X) :- _variable_multipleDeclarations(LBL,X,D).
_variable_multiple(LBL,X) :- _variable_multipleDefinitions(LBL,X,D).
_passed(correction(multipleDeclarations,rem),LBL,DECL) :- _variable_multiple(LBL,X), _passed(sugar,LBL,DECL), DECL=variable_declare(X,D).
_passed(correction(multipleDeclarations,rem),LBL,DECL) :- _variable_multiple(LBL,X), _passed(sugar,LBL,DECL), DECL=variable_define(X,D).
_passed(correction(multipleDeclarations,rem),LBL,DECL) :- _variable_multiple(LBL,X), _passed(sugar,LBL,DECL), DECL=variable_domain(X,D).
_passed(correction(multipleDeclarations,rem),LBL,DECL) :- _variable_multiple(LBL,X), _passed(sugar,LBL,DECL), DECL=set_assign(X,D).
_passed(correction(multipleDeclarations,rem),LBL,DECL) :- _variable_multiple(LBL,X), _passed(sugar,LBL,DECL), DECL=set_baseDomain(X,D).
_passed(correction(multipleDeclarations,rem),LBL,DECL) :- _variable_multiple(LBL,X), _passed(sugar,LBL,DECL), DECL=multimap_assign(X,D,E).
_passed(correction(multipleDeclarations,add),LBL,variable_declare(X,definition)) :- _variable_multiple(LBL,X).
_passed(correction(multipleDeclarations,add),LBL,variable_define(X,bad)) :- _variable_multiple(LBL,X).

_warning(variable(multipleDeclarations),(LBL0,(LBL1,())),(X,D0,D1)) :-
  _variable_multipleDeclarations(LBL1,X,D1),
  _passed(defaultArgs,LBL0,variable_declare(X,D0)), (LBL0,D0) < (LBL1,D1).

_warning(variable(multipleDefinitions),(LBL0,(LBL1,())),(X,E0,E1)) :-
  _variable_multipleDefinitions(LBL1,X,E1),
  _passed(defaultArgs,LBL0,variable_define(X,E0)), (LBL0,E0) < (LBL1,E1).
