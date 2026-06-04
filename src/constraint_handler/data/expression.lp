_expression(PHASE,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=bool_evaluate(E).
_expression(PHASE,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=ensure(E).
_expression(PHASE,DECL,operation(OP,ARGS)) :- _passed(PHASE,LBL,DECL), DECL=evaluate(OP,ARGS).

_expression(PHASE,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=variable_define(X,E).
_expression(PHASE,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=variable_domain(X,E).
_expression(PHASE,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=set_assign(X,E).
_expression(PHASE,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=set_baseDomain(X,E).
_expression(PHASE,DECL,(K;B)) :- _passed(PHASE,LBL,DECL), DECL=multimap_assign(X,K,B).
_expression(PHASE,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=optimize_maximizeSum(E,X,P).
_expression(PHASE,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=optimize_precision(E,PRIO).
_expression(PHASE,DECL,E) :- _passed(PHASE,LBL,DECL), DECL=preference_holds(E,K).

_expression(PHASE,E) :- _expression(PHASE,DECL,E).
_expression(PHASE,D) :- _expression(PHASE,operation(O,L)), D=@pythonListElements(L).
_expression(PHASE,D) :- _expression(PHASE,T), D=@pythonTupleElements(T).

_variable(PHASE,X) :- _expression(PHASE,variable(X)).
_variable(PHASE,X) :- _passed(PHASE,LBL,variable_domain(X,E)).
_variable(PHASE,X) :- _passed(PHASE,LBL,set_assign(X,E)).
_variable(PHASE,X) :- _passed(PHASE,LBL,set_baseDomain(X,E)).
_variable(PHASE,X) :- _passed(PHASE,LBL,multimap_assign(X,K,B)).

_isTuple(PHASE,E,N,ARGS) :- _expression(PHASE,E), true=@pythonIsTuple(E), (function,(),N,ARGS)=@pythonReify(E).
_expression_tupleLength(PHASE,E,N) :- _isTuple(PHASE,E,N,ARGS).
_expression_tupleIndex(PHASE,E,IDX,X) :- _isTuple(PHASE,E,N,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).
_expression_operationOperator(PHASE,operation(OP,ARGS),OP) :- _expression(PHASE,operation(OP,ARGS)).
_expression_operationLength(PHASE,operation(OP,ARGS),N) :- _expression(PHASE,operation(OP,ARGS)), N=@pythonListLength(ARGS).
_expression_operationIndex(PHASE,operation(OP,ARGS),IDX,X) :- _expression(PHASE,operation(OP,ARGS)), (IDX,X)=@pythonEnumerateElements(ARGS).
_expression_sequenceLength(PHASE,E,N) :- _expression_sequence(PHASE,E), N=@pythonListLength(E).
_expression_sequenceIndex(PHASE,E,IDX,X) :- _expression_sequence(PHASE,E), (IDX,X)=@pythonEnumerateElements(E).
#defined _expression_sequence/2.
