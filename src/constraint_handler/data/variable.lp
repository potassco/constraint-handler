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

% TODO var unreliably there in statement if it's in a branch (the issue arises because let in and assign are conflated)

_warning(variable(badValue),(),X) :- _se_value(variable(X),bad).
