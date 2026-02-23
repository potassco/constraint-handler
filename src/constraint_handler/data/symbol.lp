operator_declare(OP,(T,(T,())),bool) :- T = symbol, OP = (eq;neq).
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=eq,  ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 =  V2.
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=neq, ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 != V2.
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=leq, ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 <= V2.
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=lt,  ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 <  V2.
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=geq, ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 >= V2.
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=gt,  ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 >  V2.

_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=eq,  ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 != V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=neq, ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 =  V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=leq, ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 >  V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=lt,  ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 >= V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=geq, ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 <  V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=gt,  ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 <= V2.
