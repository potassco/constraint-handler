operator_declare(OP,(T,(T,())),bool) :- T = symbol, OP = (leq;lt;geq;gt).

_computedIdx(E,val(bool,true))  :- _computeIdx(E, leq), _computeIdx(E, 0, val(symbol, V1)), _computeIdx(E, 1, val(symbol, V2)), V1 <= V2.
_computedIdx(E,val(bool,true))  :- _computeIdx(E, lt),  _computeIdx(E, 0, val(symbol, V1)), _computeIdx(E, 1, val(symbol, V2)), V1 < V2.
_computedIdx(E,val(bool,true))  :- _computeIdx(E, geq), _computeIdx(E, 0, val(symbol, V1)), _computeIdx(E, 1, val(symbol, V2)), V1 >= V2.
_computedIdx(E,val(bool,true))  :- _computeIdx(E, gt),  _computeIdx(E, 0, val(symbol, V1)), _computeIdx(E, 1, val(symbol, V2)), V1 > V2.
_computedIdx(E,val(bool,false)) :- _computeIdx(E, leq), _computeIdx(E, 0, val(symbol, V1)), _computeIdx(E, 1, val(symbol, V2)), V1 > V2.
_computedIdx(E,val(bool,false)) :- _computeIdx(E, lt),  _computeIdx(E, 0, val(symbol, V1)), _computeIdx(E, 1, val(symbol, V2)), V1 >= V2.
_computedIdx(E,val(bool,false)) :- _computeIdx(E, geq), _computeIdx(E, 0, val(symbol, V1)), _computeIdx(E, 1, val(symbol, V2)), V1 < V2.
_computedIdx(E,val(bool,false)) :- _computeIdx(E, gt),  _computeIdx(E, 0, val(symbol, V1)), _computeIdx(E, 1, val(symbol, V2)), V1 <= V2.
