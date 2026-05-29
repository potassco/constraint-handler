_expression(PHASE,E) :- _passed(PHASE,bool_evaluate(LBL,E)).
_expression(PHASE,E) :- _passed(PHASE,ensure(LBL,E)).
_expression(PHASE,operation(OP,ARGS)) :- _passed(PHASE,evaluate(LBL,OP,ARGS)).

%_expression(PHASE,E) :- _passed(PHASE,variable_declare(LBL,X,fromList(L))), E=@pythonListElements(L).
_expression(PHASE,E) :- _passed(PHASE,variable_define(LBL,X,E)).
_expression(PHASE,E) :- _passed(PHASE,variable_domain(LBL,X,E)).
_expression(PHASE,E) :- _passed(PHASE,set_assign(LBL,X,E)).
_expression(PHASE,E) :- _passed(PHASE,set_baseDomain(LBL,X,E)).
_expression(PHASE,(K;B)) :- _passed(PHASE,multimap_assign(LBL,X,K,B)).
_expression(PHASE,E) :- _passed(PHASE,optimize_maximizeSum(LBL,E,X,P)).
_expression(PHASE,E) :- _passed(PHASE,optimize_precision(LBL,E,PRIO)).
_expression(PHASE,E) :- _passed(PHASE,preference_holds(LBL,E,K)).
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
_expression_operationOperator(PHASE,E,OP) :- _expression(PHASE,E), E=operation(OP,ARGS).
_expression_operationLength(PHASE,E,N) :- _expression(PHASE,E), E=operation(OP,ARGS), N=@pythonListLength(ARGS).
_expression_operationIndex(PHASE,E,IDX,X) :- _expression(PHASE,E), E=operation(OP,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).
_expression_sequenceLength(PHASE,E,N) :- _expression_sequence(PHASE,E), N=@pythonListLength(E).
_expression_sequenceIndex(PHASE,E,IDX,X) :- _expression_sequence(PHASE,E), (IDX,X)=@pythonEnumerateElements(E).
#defined _expression_sequence/2.