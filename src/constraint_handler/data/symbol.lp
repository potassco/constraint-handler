operator_declare(OP,(T,(T,())),bool) :- T = symbol, OP = (leq;lt;geq;gt).

_computedIdx_id(E_ID,val(bool,true))  :- _computeIdx_id(E_ID, leq), _computeIdx_id(E_ID, 0, val(symbol, V1)), _computeIdx_id(E_ID, 1, val(symbol, V2)), V1 <= V2.
_computedIdx_id(E_ID,val(bool,true))  :- _computeIdx_id(E_ID, lt),  _computeIdx_id(E_ID, 0, val(symbol, V1)), _computeIdx_id(E_ID, 1, val(symbol, V2)), V1 < V2.
_computedIdx_id(E_ID,val(bool,true))  :- _computeIdx_id(E_ID, geq), _computeIdx_id(E_ID, 0, val(symbol, V1)), _computeIdx_id(E_ID, 1, val(symbol, V2)), V1 >= V2.
_computedIdx_id(E_ID,val(bool,true))  :- _computeIdx_id(E_ID, gt),  _computeIdx_id(E_ID, 0, val(symbol, V1)), _computeIdx_id(E_ID, 1, val(symbol, V2)), V1 > V2.
_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, leq), _computeIdx_id(E_ID, 0, val(symbol, V1)), _computeIdx_id(E_ID, 1, val(symbol, V2)), V1 > V2.
_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, lt),  _computeIdx_id(E_ID, 0, val(symbol, V1)), _computeIdx_id(E_ID, 1, val(symbol, V2)), V1 >= V2.
_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, geq), _computeIdx_id(E_ID, 0, val(symbol, V1)), _computeIdx_id(E_ID, 1, val(symbol, V2)), V1 < V2.
_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, gt),  _computeIdx_id(E_ID, 0, val(symbol, V1)), _computeIdx_id(E_ID, 1, val(symbol, V2)), V1 <= V2.
