%%%%%%%%%%%%%%%%% _expression_query from ensure evaluate
_expression_query((),E) :- _passed(defaultArgs,ensure(LBL,E)).
_expression_query((),operation(OP,ARGS)) :- _passed(defaultArgs,evaluate(LBL,OP,ARGS)).

%%%%%%%%%%%%%%%%% _expression_query from variables
_expression_query((),E) :- _passed(defaultArgs,variable_define(LBL,X,E)).
_expression_query((),E) :- _variable_tentativeDomain(LBL,X,E).

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
%_expression_wellformed(val(T,V)) :- _expression_query(SCOPE,val(T,V)), __version(wellformed,asp).
%_expression_wellformed(variable(X)) :- _expression_query(SCOPE,variable(X)), __version(wellformed,asp).
%_expression_wellformed(()) :- _expression_query(SCOPE,()), __version(wellformed,asp).
%_expression_poorlyformed(operation(O,L)) :- _expression_query(SCOPE,operation(O,L)), D=@pythonListElements(L), not _expression_wellformed(D), __version(wellformed,asp).
%_expression_wellformed(EXPR) :- _expression_query(SCOPE,EXPR), EXPR=operation(O,L), true=@pythonIsList(L), not _expression_poorlyformed(T) :- _expression_query(SCOPE,T), D=@pythonTupleElements(T), _expression_poorlyformed(D), __version(wellformed,asp).
%_expression_wellformed(EXPR) :- _expression_query(SCOPE,EXPR), true=@pythonIsTuple(EXPR), not _expression_poorlyformed(EXPR), __version(wellformed,asp).
%_expression_poorlyformed(EXPR), __version(wellformed,asp).
%_expression_wellformed(lambda(ARGS,E)) :- _expression_query(SCOPE,lambda(ARGS,E)), __version(wellformed,asp).
%_warning(expression(syntaxError),SCOPE,"lambda checks unsupported") :- _expression_query(SCOPE,lambda(ARGS,E)), __version(wellformed,asp). % TODO

_expression_wellformed(EXPR) :- _expression_query(SCOPE,EXPR), __version(wellformed,skip).
_expression_wellformed(EXPR) :- _expression_query(SCOPE,EXPR), true=@pythonIsExpr(EXPR), __version(wellformed,python).



_expression_wellformed(bad) :- _expression_query(SCOPE,bad), __version(wellformed,positive).
_expression_wellformed(python(CODE)) :- _expression_query(SCOPE,python(CODE)), true=@pythonIsString(CODE), __version(wellformed,positive).
_expression_wellformed(val(T,V)) :- _expression_query(SCOPE,val(T,V)), __version(wellformed,positive).
_expression_wellformed(variable(X)) :- _expression_query(SCOPE,variable(X)), __version(wellformed,positive).
_expression_wellformed(()) :- _expression_query(SCOPE,()), __version(wellformed,positive).
_expression_wellformed(EXPR) :- _expression_query(SCOPE,EXPR), EXPR=operation(O,L), true=@pythonIsList(L), __version(wellformed,positive), _expression_wellformed(D) : D=@pythonListElements(L).
_expression_wellformed(EXPR) :- _expression_query(SCOPE,EXPR), true=@pythonIsTuple(EXPR), __version(wellformed,positive), _expression_wellformed(D) : D=@pythonTupleElements(EXPR).
_expression_wellformed(lambda(ARGS,E)) :- _expression_query(SCOPE,lambda(ARGS,E)), __version(wellformed,positive).
_warning(expression(syntaxError),SCOPE,"lambda checks unsupported") :- _expression_query(SCOPE,lambda(ARGS,E)), __version(wellformed,positive). %TODO

% TODO: for operations, check that the operator is well-formed

%__version(wellformed,asp).
%__version(wellformed,python).
%__version(wellformed,skip).
__version(wellformed,positive).

_warning(expression(syntaxError),SCOPE,EXPR) :- _expression_query(SCOPE,EXPR), not _expression_wellformed(EXPR).



%%%%%%%%%%%%%%%%% _expression_index _expression_isTuple
_expression_index(ARGS,IDX,X) :- _expression_query(SCOPE,E), E=operation(O,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).
_expression_isTuple(E,N,ARGS) :- _expression_query(SCOPE,E), (function,(),N,ARGS)=@pythonReify(E).
_length(ARGS,N) :- _expression_isTuple(E,N,ARGS).
_expression_index(ARGS,IDX,X) :- _expression_isTuple(E,N,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).


%%%%%%%%%%%%%%%%% _expression_safe
%_expression_safe(bad) :- _expression_wellformed(SCOPE,bad).
%_expression_safe(python(CODE)) :- _expression_wellformed(SCOPE,python(CODE)).
_expression_safe(SCOPE,EXPR) :- _expression_query(SCOPE,EXPR), _expression_wellformed(EXPR), EXPR=val(T,V).
_expression_safe(SCOPE,EXPR) :- _expression_query(SCOPE,EXPR), _expression_wellformed(EXPR), EXPR=variable(X), _variable_safe(SCOPE,X).
_expression_safe(SCOPE,EXPR) :- _expression_query(SCOPE,EXPR), _expression_wellformed(EXPR), EXPR=().
_expression_safe(SCOPE,EXPR) :- _expression_query(SCOPE,EXPR), _expression_wellformed(EXPR), EXPR=operation(O,L), _operator_safe(O), _expression_safe(SCOPE,D) : D=@pythonListElements(L).
_expression_safe(SCOPE,EXPR) :- _expression_query(SCOPE,EXPR), _expression_wellformed(EXPR), true=@pythonIsTuple(EXPR), _expression_safe(SCOPE,D) : D=@pythonTupleElements(EXPR).
%_expression_safe(lambda(ARGS,E)) :- _expression_wellformed(SCOPE,lambda(ARGS,E)).
%_warning(expression(syntaxError),SCOPE,"lambda checks unsupported") :- _expression_wellformed(SCOPE,lambda(ARGS,E)).

% TODO: for operations, check that the operator is safe?

_operator_declared(O) :- operator_declare(O,_,_).
_operator_declared(O) :- operator_declare_variadic(O,_,_,_).
_operator_unsafe(int_div;float_div).
_operator_safe(O) :- _operator_declared(O), not _operator_unsafe(O).

%_variable_unsafe((),X) :- _passed(sugar,variable_define(LBL,X,E)), not _expression_safe((),E).
%_variable_unsafe((),X) :- _passed(sugar,variable_domain(LBL,X,E)), not _expression_safe((),E).
%_variable_safe(SCOPE,X) :- _variable_query(SCOPE,X), not _variable_unsafe(SCOPE,X).
%_variable_unsafe(SCOPE,X) :- _passed(sugar,variable_define(X,E)), not _expression_safe((),E).

_variable_safe(SCOPE,X) :- _variable_query(SCOPE,X), _expression_safe((),E) : _passed(sugar,variable_define(LBL,X,E)); _expression_safe((),E) : _passed(sugar,variable_domain(LBL,X,E)).
