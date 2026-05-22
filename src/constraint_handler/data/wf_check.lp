%%%%%%%%%%%%%%%%% _expression_wellformed
_expression_query(wf_check,EXPR) :- _expression_query(sugar,EXPR).

_expression_wfQuery(EXPR) :- _expression_query(sugar,EXPR).
_expression_wellformed(bad) :- _expression_wfQuery(bad).
_expression_wellformed(python(CODE)) :- _expression_wfQuery(python(CODE)), true=@pythonIsString(CODE).
_expression_wellformed(EXPR) :- _expression_wfQuery(EXPR), EXPR=pythonExtract(PSTMT,PEXPR),true=@pythonIsString(PSTMT),true=@pythonIsString(PEXPR).
_expression_wellformed(val(T,V)) :- _expression_wfQuery(val(T,V)).
_expression_wellformed(variable(X)) :- _expression_wfQuery(variable(X)).
_expression_wellformed(EXPR) :- _expression_wfQuery(EXPR), EXPR=operation(O,L), true=@pythonIsList(L), _expression_wellformed(D) : D=@pythonListElements(L).
_expression_wellformed(EXPR) :- _expression_wfQuery(EXPR), true=@pythonIsTuple(EXPR), _expression_wellformed(D) : D=@pythonTupleElements(EXPR).
_expression_wellformed(lambda(ARGS,E)) :- _expression_wfQuery(lambda(ARGS,E)).
_warning(expression(syntaxError),(),"lambda checks unsupported") :- _expression_wfQuery(lambda(ARGS,E)). %TODO

% TODO: for operations, check that the operator is well-formed


_warning(expression(syntaxError),(),EXPR) :- _expression_query(sugar,EXPR), not _expression_wellformed(EXPR).
