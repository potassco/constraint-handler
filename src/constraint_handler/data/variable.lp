%%%%%% syntactic sugar
_passed(sugar,variable_declare(LBL,X,fromFacts)) :- _passed(defaultArgs,variable_declare(LBL,X,D)), D=(fromFacts;boolDomain;fromList(L)).
_variable_tentativeDomain(LBL,X,E) :- _passed(defaultArgs,variable_domain(LBL,X,E)).
_variable_tentativeDomain(LBL,X,E) :- _passed(defaultArgs,variable_declare(LBL,X,fromList(L))), E=@pythonListElements(L).
_variable_tentativeDomain(LBL,X,val(bool,(false;true))) :- _passed(defaultArgs,variable_declare(LBL,X,boolDomain)).
_variable_tentativeDomain(LBL,X,val(none,none)) :- _passed(defaultArgs,variable_declareOptional(LBL,X)).
_variable_tentativeDomain(LBL,X,E) :- _passed(defaultArgs,variable_domain(LBL,X,E)).
_passed(sugar,variable_domain(LBL,X,E)) :- _variable_tentativeDomain(LBL,X,E), _expression_wellformed(E).
_passed(sugar,variable_domain(LBL,X,bad)) :- _variable_tentativeDomain(LBL,X,E), not _expression_wellformed(E).
_warning(atom(syntaxError),(),variable_domain(LBL,X,E)) :- _variable_tentativeDomain(LBL,X,E), not _expression_wellformed(E).
_passed(sugar,variable_define(LBL,X,E)) :- _passed(defaultArgs,variable_define(LBL,X,E)), _expression_wellformed(E).
_passed(sugar,variable_define(LBL,X,bad)) :- _passed(defaultArgs,variable_define(LBL,X,E)), not _expression_wellformed(E).
_warning(atom(syntaxError),(),variable_define(LBL,X,E)) :- _passed(defaultArgs,variable_define(LBL,X,E)), not _expression_wellformed(E). % TODO


_variable_declared(X) :- _passed(defaultArgs,variable_declare(_,X,_)).
_passed(sugar,variable_declare(LBL,X,fromFacts)) :- _passed(defaultArgs,variable_domain(LBL,X,E)), not _variable_declared(X).
_warning(variable(undeclared),(),((),X)) :- _passed(defaultArgs,variable_domain(LBL,X,E)), not _variable_declared(X).



_warning(variable(multipleDeclarations),(CNAME1,(CNAME2,())),(X,D1,D2)) :-
  _passed(defaultArgs,variable_declare(CNAME1,X,D1)), _passed(defaultArgs,variable_declare(CNAME2,X,D2)), (CNAME1,D1) < (CNAME2,D2),
  0 = #count { CNAME3,D3 : _passed(defaultArgs,variable_declare(CNAME3,X,D3)), (CNAME3,D3) < (CNAME2,D2), (CNAME3,D3) != (CNAME1,D1) }.

_warning(variable(multipleDefinitions),(CNAME1,(CNAME2,())),(X,E1,E2)) :-
  _passed(defaultArgs,variable_define(CNAME1,X,E1)), _passed(defaultArgs,variable_define(CNAME2,X,E2)), (CNAME1,E1) < (CNAME2,E2),
  0 = #count { CNAME3,E3 : _passed(defaultArgs,variable_define(CNAME3,X,E3)), (CNAME3,E3) < (CNAME2,E2), (CNAME3,E3) != (CNAME1,E1) }.

%%% rules for compile and ground engines

_variable_declare(LBL,X) :- _passed(sugar,variable_declare(LBL,X,D)), engine(LBL,(compile;ground)).
_variable_domain(X,E) :- _passed(sugar,variable_domain(LBL,X,E)), engine(LBL,(compile;ground)).

_variable_hasDomain(X) :- _variable_domain(X,V).

direct_query(E) :- _variable_domain(X,E).
direct_query(variable(X)) :- _variable_domain(X,E).
1 { _se_value(variable(X),V) : _variable_domain(X,E), _se_value(E,V) } 1 :-
   _variable_declare(LBL,X), _variable_hasDomain(X), engine(LBL,compile).
1 { _ge_assign(LBL,X,V) : _variable_domain(X,E), _se_value(E,V) } 1 :-
   _variable_declare(LBL,X), _variable_hasDomain(X), engine(LBL,ground).
%1 { _passed(sugar,variable_define(LBL,X,V)) : _variable_domain(X,E), _se_value(E,V) } 1 :-
%   _variable_declare(LBL,X), _variable_hasDomain(X).

_warning(variable(emptyDomain),(LBL,()),X) :- _variable_declare(LBL,X), not _variable_hasDomain(X).

%%%%%%%%%%%%%%%%% _variable_query
_variable_query((),X) :- _passed(sugar,variable_domain(LABEL,X,V)).
_variable_query((),X) :- _passed(defaultArgs,set_assign(NAME,X,E)).
_variable_query((),X) :- _passed(defaultArgs,set_baseDomain(NAME,X,E)).
_variable_query((),X) :- _passed(sugar,multimap_assign(NAME,X,K,B)).
_variable_query(SCOPE,X) :- _expression_query(SCOPE,variable(X)).
_variable_query((),execution_input(NAME,X)) :- _statement_query(SCOPE,STMT), _passed(sugar,execution_declare(LBL,NAME,STMT,INS,OUTS)), X=@pythonListElements(INS).
_variable_query((NAME,()),X) :- _passed(sugar,execution_declare(LBL,NAME,STMT,INS,OUTS)), X=@pythonListElements(OUTS).

_variable_exists((),X) :- _passed(sugar,variable_declare(LBL,X,D)).
_variable_exists((),X) :- _passed(sugar,variable_define(LBL,X,E)).
_variable_exists((),X) :- _passed(sugar,set_declare(LBL,X)).
_variable_exists((),X) :- _passed(sugar,multimap_declare(LBL,X)).
_variable_exists(SCOPE,X) :- _statement_query(SCOPE,assign(X,EXPR)).
_variable_exists((NAME,()),X) :- _passed(sugar,execution_declare(LBL,NAME,STMT,INS,OUTS)), X=@pythonListElements(INS).
_variable_exists((),execution_output(NAME,X)) :- _passed(sugar,execution_declare(LBL,NAME,STMT,INS,OUTS)), X=@pythonListElements(OUTS).

_variable_search_scope(SCOPE,X) :- _variable_query(SCOPE,X).
_variable_search_scope(OUTER,X) :- _variable_search_scope(SCOPE,X), SCOPE=(_,OUTER), not _variable_exists(SCOPE,X).
_variable_found(SCOPE,X) :- _variable_search_scope(SCOPE,X), _variable_exists(SCOPE,X).
_variable_found(SCOPE,X) :- _variable_search_scope(SCOPE,X), SCOPE=(_,OUTER), _variable_found(OUTER,X).
_warning(variable(undeclared),(),(SCOPE,X)) :- _variable_query(SCOPE,X), not _variable_found(SCOPE,X).

_variable_confusingName((assert;assign;if;noop;statement_python;seq2;while),keyword). % statement
_variable_confusingName((lambda;operation;python;val;variable),keyword). % expression
_variable_confusingName((boolDomain;fromFacts;fromList),keyword). % domain
_variable_confusingName((none;bool;int;float;string;symbol;set;multimap),type).
_variable_confusingName(O,operator) :- operator_declare(O,INS,OUT).

_warning(variable(confusingName),(),((SCOPE,X),REASON)) :- _variable_exists(SCOPE,X), _variable_confusingName(BAD,REASON), (function,BAD,N,ARGS)=@pythonReify(X).
_warning(variable(confusingName),(),((SCOPE,X),number)) :- _variable_exists(SCOPE,X), (number,_,_,_)=@pythonReify(X).

% TODO var unreliably there in statement if it's in a branch (the issue arises because let in and assign are conflated)

_warning(variable(badValue),(),X) :- _se_value(variable(X),bad).
