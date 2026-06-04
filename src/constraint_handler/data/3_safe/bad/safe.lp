_main(safe).

%%%%%%%%%%%%%%%%% _expression_safe
_expression_safeQuery(EXPR) :- _main(safe), _expression(sugar,EXPR).
_expression_safe(EXPR) :- _expression_safeQuery(EXPR), EXPR=val(T,V).
_expression_safe(EXPR) :- _expression_safeQuery(EXPR), EXPR=variable(X), _variable_safe(X).
_expression_safe(EXPR) :- _expression_safeQuery(EXPR), EXPR=operation(O,L), _operator_safe(O), _expression_safe(D) : D=@pythonListElements(L).
_expression_safe(EXPR) :- _expression_safeQuery(EXPR), true=@pythonIsTuple(EXPR), _expression_safe(D) : D=@pythonTupleElements(EXPR).
%_expression_safe(lambda(ARGS,E)) :- _expression_safeQuery(lambda(ARGS,E)).
%_warning(expression(syntaxError),SCOPE,"lambda checks unsupported") :- _expression_safeQuery(SCOPE,lambda(ARGS,E)).

% TODO: for operations, check that the operator is safe?

_operator_unsafe(int_div;float_div).

%_variable_unsafe((),X) :- _passed(sugar,variable_define(LBL,X,E)), not _expression_safe((),E).
%_variable_unsafe((),X) :- _passed(sugar,variable_domain(LBL,X,E)), not _expression_safe((),E).
%_variable_safe(SCOPE,X) :- _variable_query(safe,X), not _variable_unsafe(SCOPE,X).
%_variable_unsafe(SCOPE,X) :- _passed(sugar,variable_define(X,E)), not _expression_safe((),E).

_variable_safe(X) :- _variable_query(safe,X), _expression_safe(E) : _passed(sugar,LBL,variable_define(X,E)); _expression_safe(E) : _passed(sugar,LBL,variable_domain(X,E)).
_variable_query(safe,X) :- _variable(sugar,X).



_safe_bad(bad) :- _main(safe).
_safe_bad(variable(X)) :- _main(safe), _expression(sugar,variable(X)), _passed(sugar,LBL,variable_define(X,E)), _safe_bad(E).
_safe_bad(variable(X)) :- _main(safe), _expression(sugar,variable(X)), _passed(sugar,LBL,variable_declare(X,set)), _passed(sugar,LBL2,set_assign(LBL2,X,E)), _safe_bad(E).
_safe_bad(variable(X)) :- _main(safe), _expression(sugar,variable(X)), _passed(sugar,LBL,variable_declare(X,multimap)), _passed(sugar,LBL2,multimap_assign(LBL2,X,KE,BE)), _safe_bad(KE;BE).
_safe_bad(EXPR) :- _main(safe), _expression(sugar,EXPR), _expression_tupleIndex(sugar,EXPR,IDX,F), _safe_bad(F).
%_safe_bad(EXPR) :- _main(safe), _expression(sugar,EXPR), _expression_tupleLength(EXPR,N), N > 0, _safe_bad(F) : _expression_tupleIndex(sugar,EXPR,IDX,F).
_safe_bad(EXPR) :- _main(safe), _expression(sugar,EXPR), _expression_operationIndex(sugar,EXPR,IDX,F), _safe_bad(F), _expression_operationOperator(sugar,EXPR,OP), not _operator_recoverable(OP).
_safe_bad(EXPR) :- _main(safe), _expression(sugar,EXPR), _expression_operationOperator(sugar,EXPR,OP), _safe_bad(OP).

_deterministic(E,bad) :- _safe_bad(E).
_deterministic(val(T,V),val(T,V)) :- _phase_active(constantFolding), _expression(sugar,val(T,V)).

_passed(correction(constant,rem),LBL,variable_define(X,E)) :- _deterministic(E,V), _passed(sugar,LBL,variable_define(X,E)).
_passed(correction(constant,add),LBL,variable_define(X,V)) :- _deterministic(E,V), _passed(sugar,LBL,variable_define(X,E)).
