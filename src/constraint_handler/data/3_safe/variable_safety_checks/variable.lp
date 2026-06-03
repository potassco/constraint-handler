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

% multiple dclarations
_variable_declared(X) :- _passed(defaultArgs,variable_declare(LBL,X,fromFacts)).
_passed(sugar,variable_declare(LBL,X,fromFacts)) :- _passed(defaultArgs,variable_domain(LBL,X,E)), not _variable_declared(X).
_warning(variable(undeclared),(),X) :- _passed(defaultArgs,variable_domain(LBL,X,E)), not _variable_declared(X).

_warning(variable(multipleDeclarations),(CNAME1,(CNAME2,())),(X,D1,D2)) :-
  _passed(defaultArgs,variable_declare(CNAME1,X,D1)), _passed(defaultArgs,variable_declare(CNAME2,X,D2)), (CNAME1,D1) < (CNAME2,D2),
  0 = #count { CNAME3,D3 : _passed(defaultArgs,variable_declare(CNAME3,X,D3)), (CNAME3,D3) < (CNAME2,D2), (CNAME3,D3) != (CNAME1,D1) }.

_warning(variable(multipleDefinitions),(CNAME1,(CNAME2,())),(X,E1,E2)) :-
  _passed(defaultArgs,variable_define(CNAME1,X,E1)), _passed(defaultArgs,variable_define(CNAME2,X,E2)), (CNAME1,E1) < (CNAME2,E2),
  0 = #count { CNAME3,E3 : _passed(defaultArgs,variable_define(CNAME3,X,E3)), (CNAME3,E3) < (CNAME2,E2), (CNAME3,E3) != (CNAME1,E1) }.
