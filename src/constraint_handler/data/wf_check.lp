%%%%%%%%%%%%%%%%% _expression_wellformed
_expression_query(wf_check,EXPR) :- _expression_query(sugar,EXPR).

_expression_wfQuery(EXPR) :- _expression_query(sugar,EXPR).
_expression_wellformed(bad) :- _expression_wfQuery(bad).
_expression_wellformed(python(CODE)) :- _expression_wfQuery(python(CODE)), true=@pythonIsString(CODE).
_expression_wellformed(EXPR) :- _expression_wfQuery(EXPR), EXPR=pythonExtract(PSTMT,PEXPR),true=@pythonIsString(PSTMT),true=@pythonIsString(PEXPR).
_expression_wellformed(val(T,V)) :- _expression_wfQuery(val(T,V)).
_expression_wellformed(variable(X)) :- _expression_wfQuery(variable(X)).
_expression_wellformed(()) :- _expression_wfQuery(()).
_expression_wellformed(EXPR) :- _expression_wfQuery(EXPR), EXPR=operation(O,L), true=@pythonIsList(L), _expression_wellformed(D) : D=@pythonListElements(L).
_expression_wellformed(EXPR) :- _expression_wfQuery(EXPR), true=@pythonIsTuple(EXPR), _expression_wellformed(D) : D=@pythonTupleElements(EXPR).
_expression_wellformed(lambda(ARGS,E)) :- _expression_wfQuery(lambda(ARGS,E)).
_warning(expression(syntaxError),(),"lambda checks unsupported") :- _expression_wfQuery(lambda(ARGS,E)). %TODO

% TODO: for operations, check that the operator is well-formed


_warning(expression(syntaxError),(),EXPR) :- _expression_query(sugar,EXPR), not _expression_wellformed(EXPR).


%%%%%%%%%%%%%%%%% _expression_safe
_expression_solveQuery(EXPR) :- _expression_query(wf_check,EXPR).
%_expression_safe(bad) :- _expression_wellformed(SCOPE,bad).
%_expression_safe(python(CODE)) :- _expression_wellformed(SCOPE,python(CODE)).
_expression_safe(EXPR) :- _expression_solveQuery(EXPR), _expression_wellformed(EXPR), EXPR=val(T,V).
_expression_safe(EXPR) :- _expression_solveQuery(EXPR), _expression_wellformed(EXPR), EXPR=variable(X), _variable_safe(X).
_expression_safe(EXPR) :- _expression_solveQuery(EXPR), _expression_wellformed(EXPR), EXPR=().
_expression_safe(EXPR) :- _expression_solveQuery(EXPR), _expression_wellformed(EXPR), EXPR=operation(O,L), _operator_safe(O), _expression_safe(D) : D=@pythonListElements(L).
_expression_safe(EXPR) :- _expression_solveQuery(EXPR), _expression_wellformed(EXPR), true=@pythonIsTuple(EXPR), _expression_safe(D) : D=@pythonTupleElements(EXPR).
%_expression_safe(lambda(ARGS,E)) :- _expression_wellformed(SCOPE,lambda(ARGS,E)).
%_warning(expression(syntaxError),SCOPE,"lambda checks unsupported") :- _expression_wellformed(SCOPE,lambda(ARGS,E)).

% TODO: for operations, check that the operator is safe?

_operator_unsafe(int_div;float_div).

%_variable_unsafe((),X) :- _passed(wf_check,variable_define(LBL,X,E)), not _expression_safe((),E).
%_variable_unsafe((),X) :- _passed(wf_check,variable_domain(LBL,X,E)), not _expression_safe((),E).
%_variable_safe(SCOPE,X) :- _variable_query(SCOPE,X), not _variable_unsafe(SCOPE,X).
%_variable_unsafe(SCOPE,X) :- _passed(wf_check,variable_define(X,E)), not _expression_safe((),E).

_variable_safe(X) :- _variable_query(solve,X), _expression_safe(E) : _passed(wf_check,variable_define(LBL,X,E)); _expression_safe(E) : _passed(wf_check,variable_domain(LBL,X,E)).
_variable_query(solve,X) :- _expression_solveQuery(EXPR), EXPR=variable(X).
