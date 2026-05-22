%%%%%%%%%%%%%%%%% _expression_safe
_expression_safeQuery(EXPR) :- _expression_query(wf_check,EXPR).
_expression_safe(EXPR) :- _expression_safeQuery(EXPR), _expression_wellformed(EXPR), EXPR=val(T,V).
_expression_safe(EXPR) :- _expression_safeQuery(EXPR), _expression_wellformed(EXPR), EXPR=variable(X), _variable_safe(X).
%_expression_safe(EXPR) :- _expression_safeQuery(EXPR), _expression_wellformed(EXPR), EXPR=().
_expression_safe(EXPR) :- _expression_safeQuery(EXPR), _expression_wellformed(EXPR), EXPR=operation(O,L), _operator_safe(O), _expression_safe(D) : D=@pythonListElements(L).
_expression_safe(EXPR) :- _expression_safeQuery(EXPR), _expression_wellformed(EXPR), true=@pythonIsTuple(EXPR), _expression_safe(D) : D=@pythonTupleElements(EXPR).
%_expression_safe(lambda(ARGS,E)) :- _expression_wellformed(SCOPE,lambda(ARGS,E)).
%_warning(expression(syntaxError),SCOPE,"lambda checks unsupported") :- _expression_wellformed(SCOPE,lambda(ARGS,E)).

% TODO: for operations, check that the operator is safe?

_operator_unsafe(int_div;float_div).

%_variable_unsafe((),X) :- _passed(wf_check,variable_define(LBL,X,E)), not _expression_safe((),E).
%_variable_unsafe((),X) :- _passed(wf_check,variable_domain(LBL,X,E)), not _expression_safe((),E).
%_variable_safe(SCOPE,X) :- _variable_query(SCOPE,X), not _variable_unsafe(SCOPE,X).
%_variable_unsafe(SCOPE,X) :- _passed(wf_check,variable_define(X,E)), not _expression_safe((),E).

_variable_safe(X) :- _variable_query(wf_check,X), _expression_safe(E) : _passed(wf_check,variable_define(LBL,X,E)); _expression_safe(E) : _passed(wf_check,variable_domain(LBL,X,E)).
_variable_query(wf_check,X) :- _expression_safeQuery(variable(X)).
