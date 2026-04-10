%%%%%%%%%%%%%%%%% _expression_query from evaluate
_expression_query((),operation(OP,ARGS)) :- evaluate(OP,ARGS).

%%%%%%%%%%%%%%%%% _expression_query from variables
_expression_query((),E) :- variable_define(_,X,E).
_expression_query((),E) :- variable_domain(X,E).
_expression_query((),E) :- variable_declare(_,X,fromList(L)), E=@pythonListElements(L).

_expression_query((),E) :- set_assign(_,X,E).
_expression_query((),E) :- set_baseDomain(_,X,E).
_expression_query((),K) :- multimap_assign(_,X,K,B).
_expression_query((),B) :- multimap_assign(_,X,K,B).

%%%%%%%%%%%%%%%%% _expression_query from expressions
% TODO lambda?.
_expression_query(SCOPE,D) :- _expression_query(SCOPE,operation(O,L)), D=@pythonListElements(L).
_expression_query(SCOPE,D) :- _expression_query(SCOPE,T), D=@pythonTupleElements(T).

%%%%%%%%%%%%%%%%% _expression_query from statements
_expression_query(SCOPE,EXPR) :- _statement_query(SCOPE,assert(EXPR)).
_expression_query(SCOPE,EXPR) :- _statement_query(SCOPE,assign(X,EXPR)).
_expression_query(SCOPE,EXPR) :- _statement_query(SCOPE,if(EXPR,THEN,ELSE)).
_expression_query(SCOPE,EXPR) :- _statement_query(SCOPE,while(MAX,EXPR,BODY)).

%%%%%%%%%%%%%%%%% _expression_wellformed
_expression_wellformed(val(T,V)) :- _expression_query(SCOPE,val(T,V)).
_expression_wellformed(variable(X)) :- _expression_query(SCOPE,variable(X)).
_expression_wellformed(()) :- _expression_query(SCOPE,()).
_expression_poorlyformed(operation(O,L)) :- _expression_query(SCOPE,operation(O,L)), D=@pythonListElements(L), not _expression_wellformed(D).
_expression_poorlyformed(T) :- _expression_query(SCOPE,T), D=@pythonTupleElements(T), _expression_poorlyformed(D).

_expression_wellformed(EXPR) :- _expression_query(SCOPE,EXPR), true=@pythonIsTuple(EXPR), not _expression_poorlyformed(EXPR).
_expression_wellformed(EXPR) :- _expression_query(SCOPE,EXPR), EXPR=operation(_,L), true=@pythonIsList(L), not _expression_poorlyformed(EXPR).

_warning(expression(syntax),SCOPE,EXPR) :- _expression_query(SCOPE,EXPR), not _expression_wellformed(EXPR).