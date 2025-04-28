computed(OP,ARGS,int,V1+V2) :- compute(OP,ARGS), OP=add,  ARGS = (int,(V1,(int,(V2,())))).
computed(OP,ARGS,int,V1-V2) :- compute(OP,ARGS), OP=sub,  ARGS = (int,(V1,(int,(V2,())))).
computed(OP,ARGS,int,V1*V2) :- compute(OP,ARGS), OP=mult, ARGS = (int,(V1,(int,(V2,())))).

computed(OP,ARGS,int,|V|) :- compute(OP,ARGS), OP=abs,   ARGS = (int,(V,())).
computed(OP,ARGS,int,-V)  :- compute(OP,ARGS), OP=minus, ARGS = (int,(V,())).

computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=eq,  ARGS = (int,(V1,(int,(V2,())))), V1 =  V2.
computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=neq, ARGS = (int,(V1,(int,(V2,())))), V1 != V2.
computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=leq, ARGS = (int,(V1,(int,(V2,())))), V1 <= V2.
computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=lt,  ARGS = (int,(V1,(int,(V2,())))), V1 <  V2.
computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=geq, ARGS = (int,(V1,(int,(V2,())))), V1 >= V2.
computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=gt,  ARGS = (int,(V1,(int,(V2,())))), V1 >  V2.

computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=eq,  ARGS = (int,(V1,(int,(V2,())))), V1 != V2.
computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=neq, ARGS = (int,(V1,(int,(V2,())))), V1 =  V2.
computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=leq, ARGS = (int,(V1,(int,(V2,())))), V1 >  V2.
computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=lt,  ARGS = (int,(V1,(int,(V2,())))), V1 >= V2.
computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=geq, ARGS = (int,(V1,(int,(V2,())))), V1 <  V2.
computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=gt,  ARGS = (int,(V1,(int,(V2,())))), V1 <= V2.
