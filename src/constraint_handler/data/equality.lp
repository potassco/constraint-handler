%%%%%%%%%%%%%%%%% generic eq neq
operator_declare((eq;neq),(T,(T,())),bool) :- _type_extensionalEquality(T).

_computedIdx(E,val(bool,true)) :- _computeIdx(E,eq), _computeIdx(E,0,val(T,V)), _computeIdx(E,1,val(T,V)),
    _type_extensionalEquality(T).

_computedIdx(E,val(bool,false)) :- _computeIdx(E,eq), _computeIdx(E,0,val(T,V)),
    not _computeIdx(E,1,val(T,V)), % TODO drop negation and suffer quadratic blow-up?
    _type_extensionalEquality(T).

_computedIdx(E,val(bool,false)) :- _computeIdx(E,eq), _computeIdx(E,1,val(T,V)),
    not _computeIdx(E,0,val(T,V)),
    _type_extensionalEquality(T).

_computedIdx(E,val(bool,true)) :- _computeIdx(E,neq), _computeIdx(E,0,val(T,V)),
    not _computeIdx(E,1,val(T,V)),
    _type_extensionalEquality(T).

_computedIdx(E,val(bool,true)) :- _computeIdx(E,neq), _computeIdx(E,1,val(T,V)),
    not _computeIdx(E,0,val(T,V)),
    _type_extensionalEquality(T).

_computedIdx(E,val(bool,false)) :- _computeIdx(E,neq), _computeIdx(E,0,val(T,V)), _computeIdx(E,1,val(T,V)),
    _type_extensionalEquality(T).

%%%%%%%%%%%%%%%%% tuple eq neq
%%%% Compare tuple entries through expression equality, not structural symbol equality,
%%%% so nested sets/multimaps use their dedicated eq semantics.

__computedIdx(E,val(bool,false)) :- _computeIdx(E,eq),
    _computeIdx(E,0,T0), _expression_isTuple(T0,N0,ARGS0),
    _computeIdx(E,1,T1), _expression_isTuple(T1,N1,ARGS1), N0!=N1.
__computedIdx(E,val(bool,true)) :- _computeIdx(E,neq),
    _computeIdx(E,0,T0), _expression_isTuple(T0,N0,ARGS0),
    _computeIdx(E,1,T1), _expression_isTuple(T1,N1,ARGS1), N0!=N1.

_tupleComp(E,OP,T1,T2,N) :- _computeIdx(E,OP), OP=(eq;neq),
    _computeIdx(E,0,T1), _expression_isTuple(T1,N,ARGS1),
    _computeIdx(E,1,T2), _expression_isTuple(T2,N,ARGS2).
_tuple_pair(T1,T2,IDX,X1,X2) :- _tupleComp(E,OP,T1,T2,N),
    _expression_isTuple(T1,N,ARGS1), _expression_index(ARGS1,IDX,X1),
    _expression_isTuple(T2,N,ARGS2), _expression_index(ARGS2,IDX,X2).

direct_query(operation(eq,(X1,(X2,())))) :- _tuple_pair(T1,T2,IDX,X1,X2).

_tupleEqAux(T1,T2,0) :- _tupleComp(E,(eq;neq),T1,T2,N).
_tupleEqAux(T1,T2,IDX+1) :- _tupleEqAux(T1,T2,IDX), _tuple_pair(T1,T2,IDX,X1,X2), _se_value(operation(eq,(X1,(X2,()))),val(bool,true)).
_computedIdx(E,val(bool,true))   :- _tupleComp(E,eq,T1,T2,N),  _tupleEqAux(T1,T2,N).
_computedIdx(E,val(bool,false)) :- _tupleComp(E,neq,T1,T2,N), _tupleEqAux(T1,T2,N).

_computedIdx(E,val(bool,false)) :- _tupleComp(E,eq,T1,T2,N), _tuple_pair(T1,T2,IDX,X1,X2), _se_value(operation(eq,(X1,(X2,()))),val(bool,false)).
_computedIdx(E,val(bool,true)) :- _tupleComp(E,neq,T1,T2,N), _tuple_pair(T1,T2,IDX,X1,X2), _se_value(operation(eq,(X1,(X2,()))),val(bool,false)).


%%%%%%%%%%%%%%%%% generic leq lt geq gt
operator_declare((leq;lt;geq;gt),(T,(T,())),bool) :- _type_extensionalOrder(T).
_computedIdx(E,val(bool,true))  :- _computeIdx(E,leq), _computeIdx(E,0,val(T,V1)), _computeIdx(E,1,val(T,V2)),
    V1 <= V2,
    _type_extensionalOrder(T).
_computedIdx(E,val(bool,true))  :- _computeIdx(E,lt),  _computeIdx(E,0,val(T,V1)), _computeIdx(E,1,val(T,V2)),
    V1 < V2,
    _type_extensionalOrder(T).
_computedIdx(E,val(bool,true))  :- _computeIdx(E,geq), _computeIdx(E,0,val(T,V1)), _computeIdx(E,1,val(T,V2)),
    V1 >= V2,
    _type_extensionalOrder(T).
_computedIdx(E,val(bool,true))  :- _computeIdx(E,gt),  _computeIdx(E,0,val(T,V1)), _computeIdx(E,1,val(T,V2)),
    V1 > V2,
    _type_extensionalOrder(T).
_computedIdx(E,val(bool,false)) :- _computeIdx(E,leq), _computeIdx(E,0,val(T,V1)), _computeIdx(E,1,val(T,V2)),
    V1 > V2,
    _type_extensionalOrder(T).
_computedIdx(E,val(bool,false)) :- _computeIdx(E,lt),  _computeIdx(E,0,val(T,V1)), _computeIdx(E,1,val(T,V2)),
    V1 >= V2,
    _type_extensionalOrder(T).
_computedIdx(E,val(bool,false)) :- _computeIdx(E,geq), _computeIdx(E,0,val(T,V1)), _computeIdx(E,1,val(T,V2)),
    V1 < V2,
    _type_extensionalOrder(T).
_computedIdx(E,val(bool,false)) :- _computeIdx(E,gt),  _computeIdx(E,0,val(T,V1)), _computeIdx(E,1,val(T,V2)),
    V1 <= V2,
    _type_extensionalOrder(T).
