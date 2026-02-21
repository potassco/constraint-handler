operator_declare(OP,(T,(T,())),bool) :- T = symbol, OP = (eq;neq).
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=eq,  ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 =  V2.
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=neq, ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 != V2.
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=leq, ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 <= V2.
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=lt,  ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 <  V2.
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=geq, ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 >= V2.
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=gt,  ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 >  V2.

computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=eq,  ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 != V2.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=neq, ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 =  V2.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=leq, ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 >  V2.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=lt,  ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 >= V2.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=geq, ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 <  V2.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=gt,  ARGS = (val(symbol,V1),(val(symbol,V2),())), V1 <= V2.
