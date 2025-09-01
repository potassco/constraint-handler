computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=eq,  ARGS = (symbol,(V1,(symbol,(V2,())))), V1 =  V2.
computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=neq, ARGS = (symbol,(V1,(symbol,(V2,())))), V1 != V2.
computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=leq, ARGS = (symbol,(V1,(symbol,(V2,())))), V1 <= V2.
computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=lt,  ARGS = (symbol,(V1,(symbol,(V2,())))), V1 <  V2.
computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=geq, ARGS = (symbol,(V1,(symbol,(V2,())))), V1 >= V2.
computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=gt,  ARGS = (symbol,(V1,(symbol,(V2,())))), V1 >  V2.

computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=eq,  ARGS = (symbol,(V1,(symbol,(V2,())))), V1 != V2.
computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=neq, ARGS = (symbol,(V1,(symbol,(V2,())))), V1 =  V2.
computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=leq, ARGS = (symbol,(V1,(symbol,(V2,())))), V1 >  V2.
computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=lt,  ARGS = (symbol,(V1,(symbol,(V2,())))), V1 >= V2.
computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=geq, ARGS = (symbol,(V1,(symbol,(V2,())))), V1 <  V2.
computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=gt,  ARGS = (symbol,(V1,(symbol,(V2,())))), V1 <= V2.
