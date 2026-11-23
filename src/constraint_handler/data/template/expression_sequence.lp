_isTuple(PHASE,E) :- _expression(PHASE,E), true=@pythonIsTuple(E).
_isTuple(PHASE,E,N,ARGS) :- _isTuple(PHASE,E), (function,(),N,ARGS)=@pythonReify(E).

_expression_tupleLength(PHASE,E,N) :- _isTuple(PHASE,E,N,ARGS).
_expression_tupleIndex(PHASE,E,0,E0) :- _isTuple(PHASE,E,N,(E0,TAIL)).
_expression_tupleIndex(PHASE,E,1,E1) :- _isTuple(PHASE,E,N,(E0,(E1,TAIL))).
_expression_tupleIndex(PHASE,E,2,E2) :- _isTuple(PHASE,E,N,(E0,(E1,(E2,TAIL)))).
_expression_tupleIndex(PHASE,E,IDX+3,X) :- _isTuple(PHASE,E,N,(E0,(E1,(E2,TAIL)))), (IDX,X)=@pythonEnumerateElements(TAIL).
_expression_operationOperator(PHASE,operation(OP,ARGS),OP) :- _expression(PHASE,operation(OP,ARGS)).
_expression_operationLength(PHASE,operation(OP,()),0) :- _expression(PHASE,operation(OP,())).
_expression_operationLength(PHASE,operation(OP,(E0,())),1) :- _expression(PHASE,operation(OP,(E0,()))).
_expression_operationLength(PHASE,operation(OP,(E0,(E1,()))),2) :- _expression(PHASE,operation(OP,(E0,(E1,())))).
_expression_operationLength(PHASE,operation(OP,(E0,(E1,(E2,TAIL)))),N+3) :- _expression(PHASE,operation(OP,(E0,(E1,(E2,TAIL))))), N=@pythonListLength(TAIL).
_expression_operationIndex(PHASE,operation(OP,(E0,TAIL)),0,E0) :- _expression(PHASE,operation(OP,(E0,TAIL))).
_expression_operationIndex(PHASE,operation(OP,(E0,(E1,TAIL))),1,E1) :- _expression(PHASE,operation(OP,(E0,(E1,TAIL)))).
_expression_operationIndex(PHASE,operation(OP,(E0,(E1,(E2,TAIL)))),2,E2) :- _expression(PHASE,operation(OP,(E0,(E1,(E2,TAIL))))).
_expression_operationIndex(PHASE,operation(OP,(E0,(E1,(E2,TAIL)))),IDX+3,X) :- _expression(PHASE,operation(OP,(E0,(E1,(E2,TAIL))))), (IDX,X)=@pythonEnumerateElements(TAIL).
_expression_sequenceLength(PHASE,(),0) :- _expression_sequence(PHASE,()).
_expression_sequenceLength(PHASE,(E0,()),1) :- _expression_sequence(PHASE,(E0,())).
_expression_sequenceLength(PHASE,(E0,(E1,())),2) :- _expression_sequence(PHASE,(E0,(E1,()))).
_expression_sequenceLength(PHASE,(E0,(E1,(E2,TAIL))),N+3) :- _expression_sequence(PHASE,(E0,(E1,(E2,TAIL)))), N=@pythonListLength(TAIL).
_expression_sequenceIndex(PHASE,(E0,TAIL),0,E0) :- _expression_sequence(PHASE,(E0,TAIL)).
_expression_sequenceIndex(PHASE,(E0,(E1,TAIL)),1,E1) :- _expression_sequence(PHASE,(E0,(E1,TAIL))).
_expression_sequenceIndex(PHASE,(E0,(E1,(E2,TAIL))),2,E2) :- _expression_sequence(PHASE,(E0,(E1,(E2,TAIL)))).
_expression_sequenceIndex(PHASE,(E0,(E1,(E2,TAIL))),IDX+3,X) :- _expression_sequence(PHASE,(E0,(E1,(E2,TAIL)))), (IDX,X)=@pythonEnumerateElements(TAIL).
#defined _expression_sequence/2.
