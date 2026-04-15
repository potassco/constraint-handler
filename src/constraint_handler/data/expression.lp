%%%%%%%%%%%%%%%%% _expression_query from ensure evaluate
_expression_query((),E) :- ensure(LBL,E).
_expression_query((),operation(OP,ARGS)) :- evaluate(LBL,OP,ARGS).

%%%%%%%%%%%%%%%%% _expression_query from variables
_expression_query((),E) :- variable_define(LBL,X,E).
_expression_query((),E) :- variable_domain(LBL,X,E).

_expression_query((),E) :- set_assign(LBL,X,E).
_expression_query((),E) :- set_baseDomain(LBL,X,E).
_expression_query((),K) :- multimap_assign(LBL,X,K,B).
_expression_query((),B) :- multimap_assign(LBL,X,K,B).

%%%%%%%%%%%%%%%%% _expression_query from other declarations
_expression_query((),E) :- optimize_maximizeSum(LBL,E,X,P).
_expression_query((),E) :- _passed(defaultArgs,optimize_precision(E,PRIO)).

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
_expression_wellformed(EXPR) :- _expression_query(SCOPE,EXPR), EXPR=operation(O,L), true=@pythonIsList(L), not _expression_poorlyformed(EXPR).

_warning(expression(syntaxError),SCOPE,EXPR) :- _expression_query(SCOPE,EXPR), not _expression_wellformed(EXPR).

_expression_wellformed(lambda(ARGS,E)) :- _expression_query(SCOPE,lambda(ARGS,E)).
_warning(expression(syntaxError),SCOPE,"lambda checks unsupported") :- _expression_query(SCOPE,lambda(ARGS,E)). % TODO
