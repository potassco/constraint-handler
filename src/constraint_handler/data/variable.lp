_variable_hasDomain(sugar,X) :- _passed(sugar,variable_domain(LBL,X,E)).
_warning(variable(emptyDomain),(LBL,()),X) :- _passed(sugar,variable_declare(LBL,X,fromFacts)), not _variable_hasDomain(sugar,X).


%%%%%%%%%%%%%%%%% _variable_query
%_variable_query(sugar,X) :- _passed(sugar,variable_domain(LABEL,X,V)).
%_variable_query(sugar,X) :- _passed(sugar,set_assign(NAME,X,E)).
%_variable_query(sugar,X) :- _passed(sugar,set_baseDomain(NAME,X,E)).
%_variable_query(sugar,X) :- _passed(sugar,multimap_assign(NAME,X,K,B)).

_variable_exists(sugar,X) :- _passed(sugar,variable_declare(LBL,X,D)).

%_variable(sugar,X) :- _variable_query(sugar,X).
_warning(variable(undeclared),(),X) :- _variable(sugar,X), not _variable_exists(sugar,X).
_passed(correction(add),_internal0,variable_declare(_internal0,X,definition)) :- _variable(sugar,X), not _variable_exists(sugar,X).
_passed(correction(add),_internal0,variable_define(_internal0,X,bad)) :- _variable(sugar,X), not _variable_exists(sugar,X).


_variable_confusingName((assert;assign;if;noop;statement_python;seq2),keyword). % statement
_variable_confusingName((lambda;operation;python;val;variable),keyword). % expression
_variable_confusingName((boolDomain;fromFacts;fromList),keyword). % domain
_variable_confusingName((none;bool;int;float;string;symbol;set;multimap),type).
_variable_confusingName(O,operator) :- _operator_declared(O).

_warning(variable(confusingName),(),(X,REASON)) :- _variable_exists(sugar,X), _variable_confusingName(BAD,REASON), (function,BAD,N,ARGS)=@pythonReify(X).
_warning(variable(confusingName),(),(X,number)) :- _variable_exists(sugar,X), (number,_,_,_)=@pythonReify(X).

_warning(variable(badValue),(),X) :- _se_value(variable(X),bad), not _statement_internalVariable(X).

%%%%%%%%%%%%%%%%% multiple declarations
_variable_multipleDeclarations(LBL1,X,D1) :-
  _passed(defaultArgs,variable_declare(LBL1,X,D1)),
  1 = #count { LBL0,D0 : _passed(defaultArgs,variable_declare(LBL0,X,D0)), (LBL0,D0) < (LBL1,D1) }.

_variable_multipleDefinitions(LBL1,X,D1) :-
  _passed(defaultArgs,variable_define(LBL1,X,D1)),
  1 = #count { LBL0,D0 : _passed(defaultArgs,variable_define(LBL0,X,D0)), (LBL0,D0) < (LBL1,D1) }.

_variable_multiple(LBL,X) :- _variable_multipleDeclarations(LBL,X,D).
_variable_multiple(LBL,X) :- _variable_multipleDefinitions(LBL,X,D).
_passed(correction(rem),DECL) :- _variable_multiple(LBL,X), _passed(sugar,DECL), DECL=variable_declare(LBL2,X,D2).
_passed(correction(rem),DECL) :- _variable_multiple(LBL,X), _passed(sugar,DECL), DECL=variable_domain(LBL2,X,D2).
_passed(correction(rem),DECL) :- _variable_multiple(LBL,X), _passed(sugar,DECL), DECL=variable_define(LBL2,X,D2).
_passed(correction(add),LBL,variable_declare(LBL,X,definition)) :- _variable_multiple(LBL,X).
_passed(correction(add),LBL,variable_define(LBL,X,bad)) :- _variable_multiple(LBL,X).

_warning(variable(multipleDeclarations),(LBL0,(LBL1,())),(X,D0,D1)) :-
  _variable_multipleDeclarations(LBL1,X,D1),
  _passed(defaultArgs,variable_declare(LBL0,X,D0)), (LBL0,D0) < (LBL1,D1).

_warning(variable(multipleDefinitions),(LBL0,(LBL1,())),(X,E0,E1)) :-
  _variable_multipleDefinitions(LBL1,X,E1),
  _passed(defaultArgs,variable_define(LBL0,X,E0)), (LBL0,E0) < (LBL1,E1).
