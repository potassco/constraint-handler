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
