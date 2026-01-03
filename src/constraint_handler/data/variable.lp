#defined variable_define/3.
#defined variable_declare/3.
#defined variable_declareOptional/1.
#defined variable_domain/2.

%%% rules common to all engines
warning(variable(undeclared),(),X) :- variable_domain(X,V), not variable_declare(_,X,_).

warning(variable(multipleDeclarations),(CNAME1,(CNAME2,())),(X,D1,D2)) :-
  variable_declare(CNAME1,X,D1), variable_declare(CNAME2,X,D2), (CNAME1,D1) < (CNAME2,D2),
  0 = #count { CNAME3,D3 : variable_declare(CNAME3,X,D3), (CNAME3,D3) < (CNAME2,D2), (CNAME3,D3) != (CNAME1,D1) }.

warning(variable(multipleDefinitions),(CNAME1,(CNAME2,())),(X,E1,E2)) :-
  variable_define(CNAME1,X,E1), variable_define(CNAME2,X,E2), (CNAME1,E1) < (CNAME2,E2),
  0 = #count { CNAME3,E3 : variable_define(CNAME3,X,E3), (CNAME3,E3) < (CNAME2,E2), (CNAME3,E3) != (CNAME1,E1) }.

%%% rules for compile and ground engines

_variable_declare(CNAME,X,D) :- variable_declare(CNAME,X,D), engine(CNAME,(compile;ground)).
_variable_define(CNAME,X,E) :- variable_define(CNAME,X,E), engine(CNAME,(compile;ground)).
assign(CNAME,X,E) :- _variable_define(CNAME,X,E).

_variable_domain(X,val(bool,(false;true))) :- _variable_declare(CNAME,X,boolDomain).
_variable_domain(X,V) :- _variable_declare(CNAME,X,fromList(L)), V=@pythonListElements(L).
_variable_domain(X,V) :- _variable_declare(CNAME,X,fromFacts), variable_domain(X,V).
_variable_domain(X,val(none,none)) :- variable_declareOptional(X), _variable_declare(CNAME,X,_).

_variable_hasDomain(X) :- _variable_domain(X,V).
1 { assign(CNAME,X,V) : _variable_domain(X,V) } 1 :-
   _variable_declare(CNAME,X,_), _variable_hasDomain(X).

warning(variable(emptyDomain),(CNAME,()),X) :- _variable_declare(CNAME,X,_), not _variable_hasDomain(X).
