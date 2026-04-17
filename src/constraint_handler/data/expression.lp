%%%%%%%%%%%%%%%%% _expression_query from ensure evaluate
_expression_query((),E) :- _passed(defaultArgs,ensure(LBL,E)).
_expression_query((),operation(OP,ARGS)) :- _passed(defaultArgs,evaluate(LBL,OP,ARGS)).

%%%%%%%%%%%%%%%%% _expression_query from variables
_expression_query((),E) :- variable_define(LBL,X,E).
_expression_query((),E) :- variable_domain(LBL,X,E).

_expression_query((),E) :- _passed(defaultArgs,set_assign(LBL,X,E)).
_expression_query((),E) :- _passed(defaultArgs,set_baseDomain(LBL,X,E)).
_expression_query((),(K;B)) :- _passed(defaultArgs,multimap_assign(LBL,X,K,B)).

%%%%%%%%%%%%%%%%% _expression_query from other declarations
_expression_query((),E) :- _passed(defaultArgs,optimize_maximizeSum(LBL,E,X,P)).
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
_expression_wellformed(val(T,V)) :- _expression_query(SCOPE,val(T,V)), __version(wellformed,asp).
_expression_wellformed(variable(X)) :- _expression_query(SCOPE,variable(X)), __version(wellformed,asp).
_expression_wellformed(()) :- _expression_query(SCOPE,()), __version(wellformed,asp).
_expression_poorlyformed(operation(O,L)) :- _expression_query(SCOPE,operation(O,L)), D=@pythonListElements(L), not _expression_wellformed(D), __version(wellformed,asp).
_expression_poorlyformed(T) :- _expression_query(SCOPE,T), D=@pythonTupleElements(T), _expression_poorlyformed(D), __version(wellformed,asp).
_expression_wellformed(EXPR) :- _expression_query(SCOPE,EXPR), true=@pythonIsTuple(EXPR), not _expression_poorlyformed(EXPR), __version(wellformed,asp).
_expression_wellformed(EXPR) :- _expression_query(SCOPE,EXPR), EXPR=operation(O,L), true=@pythonIsList(L), not _expression_poorlyformed(EXPR), __version(wellformed,asp).
_expression_wellformed(lambda(ARGS,E)) :- _expression_query(SCOPE,lambda(ARGS,E)), __version(wellformed,asp).
_warning(expression(syntaxError),SCOPE,"lambda checks unsupported") :- _expression_query(SCOPE,lambda(ARGS,E)), __version(wellformed,asp). % TODO

_expression_wellformed(EXPR) :- _expression_query(SCOPE,EXPR), __version(wellformed,skip).
_expression_wellformed(EXPR) :- _expression_query(SCOPE,EXPR), true=@pythonIsExpr(EXPR), __version(wellformed,python).

__version(wellformed,asp).
%__version(wellformed,python).
%__version(wellformed,skip).

_warning(expression(syntaxError),SCOPE,EXPR) :- _expression_query(SCOPE,EXPR), not _expression_wellformed(EXPR).
