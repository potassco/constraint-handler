_variable_multipleDeclarations(LBL1,X,D1) :-
  _passed(defaultArgs,variable_declare(LBL1,X,D1)),
  1 = #count { LBL0,D0 : _passed(defaultArgs,variable_declare(LBL0,X,D0)), (LBL0,D0) < (LBL1,D1) }.

_variable_multipleDefinitions(LBL1,X,D1) :-
  _passed(defaultArgs,variable_define(LBL1,X,D1)),
  1 = #count { LBL0,D0 : _passed(defaultArgs,variable_define(LBL0,X,D0)), (LBL0,D0) < (LBL1,D1) }.

_variable_multiple(LBL,X) :- _variable_multipleDeclarations(LBL,X,D).
_variable_multiple(LBL,X) :- _variable_multipleDefinitions(LBL,X,D).
_passed(correction(multipleDeclarations,rem),DECL) :- _variable_multiple(LBL,X), _variable_involve(sugar,X,DECL).
_passed(correction(multipleDeclarations,add),LBL,variable_declare(LBL,X,definition)) :- _variable_multiple(LBL,X).
_passed(correction(multipleDeclarations,add),LBL,variable_define(LBL,X,bad)) :- _variable_multiple(LBL,X).

_warning(variable(multipleDeclarations),(LBL0,(LBL1,())),(X,D0,D1)) :-
  _variable_multipleDeclarations(LBL1,X,D1),
  _passed(defaultArgs,variable_declare(LBL0,X,D0)), (LBL0,D0) < (LBL1,D1).

_warning(variable(multipleDefinitions),(LBL0,(LBL1,())),(X,E0,E1)) :-
  _variable_multipleDefinitions(LBL1,X,E1),
  _passed(defaultArgs,variable_define(LBL0,X,E0)), (LBL0,E0) < (LBL1,E1).
