_isTuple(PHASE,E) :- _expression(PHASE,E), true=@pythonIsTuple(E).
_isTuple(PHASE,E,N,ARGS) :- _isTuple(PHASE,E), (function,(),N,ARGS)=@pythonReify(E).

_expression_tupleLength(PHASE,E,N) :- _isTuple(PHASE,E,N,ARGS).
_expression_tupleIndex(PHASE,E,IDX,X) :- _isTuple(PHASE,E,N,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).
_expression_operationOperator(PHASE,operation(OP,ARGS),OP) :- _expression(PHASE,operation(OP,ARGS)).
_expression_operationLength(PHASE,operation(OP,ARGS),N) :- _expression(PHASE,operation(OP,ARGS)), N=@pythonListLength(ARGS).
_expression_operationIndex(PHASE,operation(OP,ARGS),IDX,X) :- _expression(PHASE,operation(OP,ARGS)), (IDX,X)=@pythonEnumerateElements(ARGS).
_expression_sequenceLength(PHASE,E,N) :- _expression_sequence(PHASE,E), N=@pythonListLength(E).
_expression_sequenceIndex(PHASE,E,IDX,X) :- _expression_sequence(PHASE,E), (IDX,X)=@pythonEnumerateElements(E).
#defined _expression_sequence/2.
