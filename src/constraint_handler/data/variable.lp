#defined variable_define/3.
#defined variable_declare/3.
#defined variable_declareOptional/1.
#defined variable_domain/2.

#show evaluated/4.
#show value/3.
#show ge_value/2.

assign(CNAME,X,E) :- variable_define(CNAME,X,E).

_variable_domain(X,val(bool,(false;true))) :- variable_declare(CNAME,X,bool).
_variable_domain(X,V) :- variable_declare(CNAME,X,fromList(L)), V=@pythonListElements(L).
_variable_domain(X,V) :- variable_declare(CNAME,X,fromFacts), variable_domain(X,V).
_variable_domain(X,val(none,none)) :- variable_declareOptional(X).

1 { assign(CNAME,X,V) : _variable_domain(X,V) } 1 :-
   variable_declare(CNAME,X,_).

warning((X,"was defined twice:",E1,E2)) :- variable_define(CNAME1,X,E1), variable_define(CNAME2,X,E2),
  (CNAME1,E1) < (CNAME2,E2).
warning((X,"was declared twice:",D1,D2)) :- variable_declare(CNAME1,X,D1), variable_declare(CNAME2,X,D2),
  (CNAME1,D1) < (CNAME2,D2).

warning((X,"has not been undeclared")) :- variable_domain(X,V), not variable_declare(_,X,_).
