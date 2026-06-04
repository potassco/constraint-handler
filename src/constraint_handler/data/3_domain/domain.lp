%%% input:
%_expression(sugar,E) with E in
% bad, val(_,_), variable(_), operation(_,_), (,...), python(_), %%% lambda(_,_), %%% ref
%
% _passed(sugar,variable_define(LBL,X,E))
% _expression_isTuple(EXPR,N,ARGS), _expression_index(ARGS,IDX,E),

%%% output:
%_expression_domain(E,V) for some expression E and a value V that is the domain of E,
%_expression_setdomain(E,V) for some expression E and a domain value V of a set expression E,
%_expression_tupledomain(EXPR,IDX,X) for some expression EXPR that is a tuple, an index IDX, and a value X that is the domain of the element at index IDX of EXPR.

%%% TODO: check performance impact of EXPR=
_expression_domain(bad,bad).
%_expression_domain(EXPR,bad) :- _expression(sugar,EXPR), EXPR=bad.
_expression_domain(EXPR,val(T,V)) :- _expression(sugar,EXPR), EXPR=val(T,V).
_expression_domain(EXPR,V) :- _expression(sugar,EXPR), EXPR=variable(X), _passed(sugar,LBL,variable_define(X,E2)), _expression_domain(E2,V).
_expression_domain(EXPR,V) :- _expression(sugar,EXPR), EXPR=variable(X), _passed(sugar,LBL,variable_domain(X,E2)), _expression_domain(E2,V).

_expression_tupleDomainAux(EXPR,N,()) :- _expression(sugar,EXPR), _expression_tupleLength(sugar,EXPR,N), #false.
_expression_tupleDomainAux(EXPR,IDX,(V,L)) :- _expression_tupleDomainAux(EXPR,IDX+1,L), _expression_tupleIndex(sugar,EXPR,IDX,E), _expression_domain(E,V).
_expression_domain(EXPR,TUPLE) :- _expression_tupleDomainAux(EXPR,0,L), TUPLE=@pythonReflect(function,(),L).

_expression_setDomainQuery(EXPR,X) :- _expression(sugar,EXPR), EXPR=variable(X), _passed(sugar,LBL,variable_declare(X,set)), #false.
_expression_setExpr(EXPR,X,assign,E) :- _expression_setDomainQuery(EXPR,X), _passed(sugar,LBL,set_assign(X,E)).
_expression_setExpr(EXPR,X,baseDomain,E) :- _expression_setDomainQuery(EXPR,X), _passed(sugar,LBL,set_baseDomain(X,E)), not _expression_setExpr(EXPR,X,assign,E).
_expression_setExprIndex(EXPR,X,-1,assign,#inf) :- _expression_setDomainQuery(EXPR,X).
_expression_setExprIndex(EXPR,X,N,baseDomain,#sup) :- _expression_setDomainQuery(EXPR,X), N=#count { E : _expression_setExpr(EXPR,X,KIND,E) }.
_expression_setExprIndex(EXPR,X,N+1,KF,F) :- _expression_setExprIndex(EXPR,X,N,KE,E), _expression_setExpr(EXPR,X,KF,F), (KE,E)<(KF,F), 0=#count { G : _expression_setExpr(EXPR,X,KG,G), (KE,E)<(KG,G), (KG,G)<(KF,F) }.
_expression_setDomain(EXPR,X,0,()) :- _expression_setDomainQuery(EXPR,X).
_expression_setDomain(EXPR,X,N+1,(V,L)) :- _expression_setDomain(EXPR,X,N,L), _expression_setExprIndex(EXPR,X,N,KE,E), _expression_domain(E,V).
_expression_setDomain(EXPR,X,N+1,L) :- _expression_setDomain(EXPR,X,N,L), _expression_setExprIndex(EXPR,X,N,baseDomain,E).
_expression_domain(EXPR,set(L)) :- _expression_setDomain(EXPR,X,N,L), _expression_setExprIndex(EXPR,X,N,baseDomain,#sup).

%_expression_setdomain(EXPR,V) :- _expression(sugar,EXPR), EXPR=variable(X), _passed(sugar,set_declare(LBL,X)), _passed(sugar,set_assign(LBL2,X,E)), _expression_domain2(E,V).
%_expression_setdomain(EXPR,V) :- _expression(sugar,EXPR), EXPR=variable(X), _passed(sugar,set_declare(LBL,X)), _passed(sugar,set_baseDomain(LBL2,X,E)), _expression_domain2(E,V).
