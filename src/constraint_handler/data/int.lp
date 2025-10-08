computed(OP,ARGS,val(int,V1+V2))  :- compute(OP,ARGS), OP=add,  ARGS = (val(int,V1),(val(int,V2),())).
computed(OP,ARGS,val(int,V1-V2))  :- compute(OP,ARGS), OP=sub,  ARGS = (val(int,V1),(val(int,V2),())).
computed(OP,ARGS,val(int,V1*V2))  :- compute(OP,ARGS), OP=mult, ARGS = (val(int,V1),(val(int,V2),())).
computed(OP,ARGS,val(int,V1/V2))  :- compute(OP,ARGS), OP=div,  ARGS = (val(int,V1),(val(int,V2),())).
computed(OP,ARGS,val(int,V1**V2)) :- compute(OP,ARGS), OP=pow,  ARGS = (val(int,V1),(val(int,V2),())).

computed(OP,ARGS,val(int,|V|)) :- compute(OP,ARGS), OP=abs,   ARGS = (val(int,V),()).
computed(OP,ARGS,val(int,-V))  :- compute(OP,ARGS), OP=minus, ARGS = (val(int,V),()).

computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=eq,  ARGS = (val(int,V1),(val(int,V2),())), V1 =  V2.
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=neq, ARGS = (val(int,V1),(val(int,V2),())), V1 != V2.
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=leq, ARGS = (val(int,V1),(val(int,V2),())), V1 <= V2.
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=lt,  ARGS = (val(int,V1),(val(int,V2),())), V1 <  V2.
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=geq, ARGS = (val(int,V1),(val(int,V2),())), V1 >= V2.
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=gt,  ARGS = (val(int,V1),(val(int,V2),())), V1 >  V2.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=eq,  ARGS = (val(int,V1),(val(int,V2),())), V1 != V2.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=neq, ARGS = (val(int,V1),(val(int,V2),())), V1 =  V2.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=leq, ARGS = (val(int,V1),(val(int,V2),())), V1 >  V2.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=lt,  ARGS = (val(int,V1),(val(int,V2),())), V1 >= V2.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=geq, ARGS = (val(int,V1),(val(int,V2),())), V1 <  V2.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=gt,  ARGS = (val(int,V1),(val(int,V2),())), V1 <= V2.
