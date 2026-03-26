operator_declare((eq;neq),(symbol,(symbol,())),bool).
_computed(eq,(val(symbol,V1),(val(symbol,V2),())),val(bool,true))   :- _compute(eq,(val(symbol,V1),(val(symbol,V2),()))), V1 =  V2.
_computed(neq,(val(symbol,V1),(val(symbol,V2),())),val(bool,true))  :- _compute(neq,(val(symbol,V1),(val(symbol,V2),()))),V1 != V2.
_computed(eq,(val(symbol,V1),(val(symbol,V2),())),val(bool,false))  :- _compute(eq,(val(symbol,V1),(val(symbol,V2),()))), V1 != V2.
_computed(neq,(val(symbol,V1),(val(symbol,V2),())),val(bool,false)) :- _compute(neq,(val(symbol,V1),(val(symbol,V2),()))),V1 =  V2.

operator_declare((leq;lt;geq;gt),(symbol,(symbol,())),bool).
_computedIdx(E,val(bool,true))  :- _computeIdx(E,leq), _computeIdx(E,0,val(symbol,V1)), _computeIdx(E,1,val(symbol,V2)), V1 <= V2.
_computedIdx(E,val(bool,true))  :- _computeIdx(E,lt),  _computeIdx(E,0,val(symbol,V1)), _computeIdx(E,1,val(symbol,V2)), V1 < V2.
_computedIdx(E,val(bool,true))  :- _computeIdx(E,geq), _computeIdx(E,0,val(symbol,V1)), _computeIdx(E,1,val(symbol,V2)), V1 >= V2.
_computedIdx(E,val(bool,true))  :- _computeIdx(E,gt),  _computeIdx(E,0,val(symbol,V1)), _computeIdx(E,1,val(symbol,V2)), V1 > V2.
_computedIdx(E,val(bool,false)) :- _computeIdx(E,leq), _computeIdx(E,0,val(symbol,V1)), _computeIdx(E,1,val(symbol,V2)), V1 > V2.
_computedIdx(E,val(bool,false)) :- _computeIdx(E,lt),  _computeIdx(E,0,val(symbol,V1)), _computeIdx(E,1,val(symbol,V2)), V1 >= V2.
_computedIdx(E,val(bool,false)) :- _computeIdx(E,geq), _computeIdx(E,0,val(symbol,V1)), _computeIdx(E,1,val(symbol,V2)), V1 < V2.
_computedIdx(E,val(bool,false)) :- _computeIdx(E,gt),  _computeIdx(E,0,val(symbol,V1)), _computeIdx(E,1,val(symbol,V2)), V1 <= V2.
