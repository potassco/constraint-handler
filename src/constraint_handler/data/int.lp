computed(OP, ARGS, val(int, 0)) :- compute(OP, ARGS), OP=add, ARGS = ().
compute(OP, TAIL) :- compute(OP, ARGS), OP=add, ARGS = (val(int, _), TAIL).
computed(OP, ARGS, val(int, V1 + VTAIL)) :- 
    compute(OP, ARGS), 
    OP=add, 
    ARGS = (val(int, V1), TAIL),
    computed(OP, TAIL, val(int, VTAIL)).

computed(OP, ARGS, val(int, 1)) :- compute(OP, ARGS), OP=mult, ARGS = ().
compute(OP, TAIL) :- compute(OP, ARGS), OP=mult, ARGS = (val(int, _), TAIL).
computed(OP, ARGS, val(int, V1 * VTAIL)) :- 
    compute(OP, ARGS), 
    OP=mult, 
    ARGS = (val(int, V1), TAIL),
    computed(OP, TAIL, val(int, VTAIL)).

computed(OP,ARGS,val(int,V1-V2))  :- compute(OP,ARGS), OP=sub,  ARGS = (val(int,V1),(val(int,V2),())).
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

computed(OP,ARGS,RES) :- compute(OP,ARGS), OP=fdiv, ARGS = (val(int,_),(val(int,_),())),
  RES = @pythonEvalExpr(operation(OP,ARGS),(),ID),
  _main_solverIdentifier(ID).
