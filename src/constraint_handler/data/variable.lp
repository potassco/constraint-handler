%%% rules for compile and ground engines

_variable_declare(LBL,X) :- _passed(wf_check,variable_declare(LBL,X,D)), engine(LBL,(compile;ground)).
_variable_domain(X,E) :- _passed(wf_check,variable_domain(LBL,X,E)), engine(LBL,(compile;ground)).

%_variable_hasDomain(X) :- _variable_domain(X,E), _expression_domain(E,V).
_variable_hasDomain(X) :- _variable_domain(X,V).

direct_query(E) :- _variable_domain(X,E).
direct_query(variable(X)) :- _variable_domain(X,E).
%1 { _se_value(variable(X),V) : _expression_domain(variable(X),V) } 1 :-
%   _variable_declare(LBL,X), _variable_hasDomain(X), engine(LBL,compile).
1 { _se_value(variable(X),V) : _variable_domain(X,E), _se_value(E,V) } 1 :-
   _variable_declare(LBL,X), _variable_hasDomain(X), engine(LBL,compile).
1 { _ge_assign(LBL,X,V) : _variable_domain(X,E), _se_value(E,V) } 1 :-
   _variable_declare(LBL,X), _variable_hasDomain(X), engine(LBL,ground).
%1 { _passed(wf_check,variable_define(LBL,X,V)) : _variable_domain(X,E), _se_value(E,V) } 1 :-
%   _variable_declare(LBL,X), _variable_hasDomain(X).

_warning(variable(emptyDomain),(LBL,()),X) :- _variable_declare(LBL,X), not _variable_hasDomain(X).


%%%%%%%%%%%%%%%%% _variable_query
_variable_query(solve,X) :- _passed(wf_check,variable_domain(LABEL,X,V)).
_variable_query(solve,X) :- _passed(wf_check,set_assign(NAME,X,E)).
_variable_query(solve,X) :- _passed(wf_check,set_baseDomain(NAME,X,E)).
_variable_query(solve,X) :- _passed(wf_check,multimap_assign(NAME,X,K,B)).
%_variable_query(solve,X) :- _expression_query(solve,variable(X)).

_variable_exists(solve,X) :- _passed(wf_check,variable_declare(LBL,X,D)).
_variable_exists(solve,X) :- _passed(wf_check,variable_define(LBL,X,E)).
_variable_exists(solve,X) :- _passed(wf_check,set_declare(LBL,X)).
_variable_exists(solve,X) :- _passed(wf_check,multimap_declare(LBL,X)).

_warning(variable(undeclared),(),X) :- _variable_query(SCOPE,X), not _variable_exists(SCOPE,X).

_variable_confusingName((assert;assign;if;noop;statement_python;seq2),keyword). % statement
_variable_confusingName((lambda;operation;python;val;variable),keyword). % expression
_variable_confusingName((boolDomain;fromFacts;fromList),keyword). % domain
_variable_confusingName((none;bool;int;float;string;symbol;set;multimap),type).
_variable_confusingName(O,operator) :- _operator_declared(O).

_warning(variable(confusingName),(),(X,REASON)) :- _variable_exists(SCOPE,X), _variable_confusingName(BAD,REASON), (function,BAD,N,ARGS)=@pythonReify(X).
_warning(variable(confusingName),(),(X,number)) :- _variable_exists(SCOPE,X), (number,_,_,_)=@pythonReify(X).

% TODO var unreliably there in statement if it's in a branch (the issue arises because let in and assign are conflated)

_warning(variable(badValue),(),X) :- _se_value(variable(X),bad).
