
%%%%%%%%%%%%%%%%% _expression_query from variables
_expression_query((),E) :- variable_define(_,X,E).
_expression_query((),E) :- variable_domain(X,E).
_expression_query((),E) :- variable_declare(_,X,fromList(L)), E=@pythonListElements(L).

_expression_query((),E) :- set_assign(_,X,E).
_expression_query((),K) :- multimap_assign(_,X,K,B).
_expression_query((),B) :- multimap_assign(_,X,K,B).

%%%%%%%%%%%%%%%%% _expression_query from expressions
% TODO tuples, lambda?.
_expression_query(SCOPE,D) :- _expression_query(SCOPE,E), E=operation(O,L), D=@pythonListElements(L).

%%%%%%%%%%%%%%%%% _expression_query from statements
_expression_query(SCOPE,EXPR) :- _statement_query(SCOPE,STMT), STMT = assert(EXPR).
_expression_query(SCOPE,EXPR) :- _statement_query(SCOPE,STMT), STMT = assign(X,EXPR).
_expression_query(SCOPE,EXPR) :- _statement_query(SCOPE,STMT), STMT = if(EXPR,THEN,ELSE).
_expression_query(SCOPE,EXPR) :- _statement_query(SCOPE,STMT), STMT = while(MAX,EXPR,BODY).

