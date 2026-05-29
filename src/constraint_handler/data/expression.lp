_expression(PHASE,DECL,E) :- _passed(PHASE,DECL), DECL=bool_evaluate(LBL,E).
_expression(PHASE,DECL,E) :- _passed(PHASE,DECL), DECL=ensure(LBL,E).
_expression(PHASE,DECL,operation(OP,ARGS)) :- _passed(PHASE,DECL), DECL=evaluate(LBL,OP,ARGS).

_expression(PHASE,DECL,E) :- _passed(PHASE,DECL), DECL=variable_define(LBL,X,E).
_expression(PHASE,DECL,E) :- _passed(PHASE,DECL), DECL=variable_domain(LBL,X,E).
_expression(PHASE,DECL,E) :- _passed(PHASE,DECL), DECL=set_assign(LBL,X,E).
_expression(PHASE,DECL,E) :- _passed(PHASE,DECL), DECL=set_baseDomain(LBL,X,E).
_expression(PHASE,DECL,(K;B)) :- _passed(PHASE,DECL), DECL=multimap_assign(LBL,X,K,B).
_expression(PHASE,DECL,E) :- _passed(PHASE,DECL), DECL=optimize_maximizeSum(LBL,E,X,P).
_expression(PHASE,DECL,E) :- _passed(PHASE,DECL), DECL=optimize_precision(LBL,E,PRIO).
_expression(PHASE,DECL,E) :- _passed(PHASE,DECL), DECL=preference_holds(LBL,E,K).

_expression(PHASE,E) :- _expression(PHASE,DECL,E).
_expression(PHASE,D) :- _expression(PHASE,operation(O,L)), D=@pythonListElements(L).
_expression(PHASE,D) :- _expression(PHASE,T), D=@pythonTupleElements(T).

_variable(PHASE,X) :- _expression(PHASE,variable(X)).
_variable(PHASE,X) :- _passed(PHASE,variable_domain(LBL,X,E)).
_variable(PHASE,X) :- _passed(PHASE,set_assign(LBL,X,E)).
_variable(PHASE,X) :- _passed(PHASE,set_baseDomain(LBL,X,E)).
_variable(PHASE,X) :- _passed(PHASE,multimap_assign(LBL,X,K,B)).

_isTuple(PHASE,E,N,ARGS) :- _expression(PHASE,E), true=@pythonIsTuple(E), (function,(),N,ARGS)=@pythonReify(E).
_expression_tupleLength(PHASE,E,N) :- _isTuple(PHASE,E,N,ARGS).
_expression_tupleIndex(PHASE,E,IDX,X) :- _isTuple(PHASE,E,N,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).
_expression_operationOperator(PHASE,operation(OP,ARGS),OP) :- _expression(PHASE,operation(OP,ARGS)).
_expression_operationLength(PHASE,operation(OP,ARGS),N) :- _expression(PHASE,operation(OP,ARGS)), N=@pythonListLength(ARGS).
_expression_operationIndex(PHASE,operation(OP,ARGS),IDX,X) :- _expression(PHASE,operation(OP,ARGS)), (IDX,X)=@pythonEnumerateElements(ARGS).
_expression_sequenceLength(PHASE,E,N) :- _expression_sequence(PHASE,E), N=@pythonListLength(E).
_expression_sequenceIndex(PHASE,E,IDX,X) :- _expression_sequence(PHASE,E), (IDX,X)=@pythonEnumerateElements(E).
#defined _expression_sequence/2.
