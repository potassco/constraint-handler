
%%%%%%%%%%%%%%%%% _expression_query from variables
_expression_query(Q,E) :- _variable_query(Q,X), variable_define(_,X,E).
_expression_query(Q,E) :- _variable_query(Q,X), variable_declare(_,X,fromFacts), variable_domain(X,E).
_expression_query(Q,E) :- _variable_query(Q,X), variable_declare(_,X,fromFList(L)), E=@pythonListElements(L).

_expression_query(Q,E) :- _variable_query(Q,X), set_declare(_,X), set_assign(_,X,E).
_expression_query(Q,K) :- _variable_query(Q,X), multimap_declare(_,X), multimap_assign(_,X,K,B).
_expression_query(Q,B) :- _variable_query(Q,X), multimap_declare(_,X), multimap_assign(_,X,K,B).

%%%%%%%%%%%%%%%%% _expression_query from expressions
% TODO tuples, lambda?.
_expression_query(Q,D) :- _expression_query(Q,E), E=operation(O,L), D=@pythonListElements(L).

%%%%%%%%%%%%%%%%% _expression_query from statements
_expression_query(Q,EXPR) :- _statement_query(Q,STMT), STMT = assert(EXPR).
_expression_query(Q,EXPR) :- _statement_query(Q,STMT), STMT = assign(VAR,EXPR).
_expression_query(Q,EXPR) :- _statement_query(Q,STMT), STMT = if(EXPR,THEN,ELSE).
_expression_query(Q,EXPR) :- _statement_query(Q,STMT), STMT = while(MAX,EXPR,BODY).

