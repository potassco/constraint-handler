%%%%%%%%%%%%%%%%% add mult
operator_declare_variadic(OP,T,T,1) :- T = int, OP = (add;mult).
_computed(OP, ARGS, val(int, 0)) :- _compute(OP, ARGS), OP=add, ARGS = ().
_compute(OP, TAIL) :- _compute(OP, ARGS), OP=add, ARGS = (val(int, _), TAIL).
_computed(OP, ARGS, val(int, V1 + VTAIL)) :-
    _compute(OP, ARGS),
    OP=add,
    ARGS = (val(int, V1), TAIL),
    _computed(OP, TAIL, val(int, VTAIL)).

% short circuit if there is a 0
_computedIdx(E,val(int,0)) :- _computeIdx(E,mult), _computeIdx(E,IDX,val(int,0)).
_computedIdx(E,val(int,1)) :- _computeIdx(E,mult), not _computeIdx(E, 0, _).
_int_mult(E,0,val(int,1)) :- _computeIdx(E,mult).
_int_mult(E,IDX+1,val(int,VO*V)) :- _computeIdx(E,mult), _computeIdx(E,IDX,val(int,V)), _int_mult(E,IDX,val(int,VO)).
_computedIdx(E,V)  :- _computeIdx(E,mult), _int_mult(E,IDX,V),_computeIdx(E,IDX-1,_), not _computeIdx(E,IDX,_).

%%%%%%%%%%%%%%%%% sub int_div pow
operator_declare(OP,(T,(T,())),T) :- T = int, OP = (sub;pow).
operator_declare(OP,(T1,(T2,())),T) :- T = int, T1 = (int;float), T2 = (int;float), OP = int_div.
_computed(OP,ARGS,val(int,V1-V2))  :- _compute(OP,ARGS), OP=sub,  ARGS = (val(int,V1),(val(int,V2),())).
_computed(OP,ARGS,val(int,V1/V2))  :- _compute(OP,ARGS), OP=int_div,  ARGS = (val(int,V1),(val(int,V2),())), V2!=0.
_computed(OP,ARGS,bad) :- _compute(OP,ARGS), OP=(int_div;float_div),  ARGS = (val(int,V1),(val(int,V2),())), V2=0.
warning(expression(zeroDivisionError),(),(OP,ARGS))  :- _compute(OP,ARGS), OP=(int_div;float_div),  ARGS = (val(int,V1),(val(int,V2),())), V2=0.
_computed(OP,ARGS,val(int,V1**V2)) :- _compute(OP,ARGS), OP=pow,  ARGS = (val(int,V1),(val(int,V2),())).

%%%%%%%%%%%%%%%%% abs minus
operator_declare(OP,(T,()),T) :- T = int, OP = (abs;minus).
_computed(OP,ARGS,val(int,|V|)) :- _compute(OP,ARGS), OP=abs,   ARGS = (val(int,V),()).
_computed(OP,ARGS,val(int,-V))  :- _compute(OP,ARGS), OP=minus, ARGS = (val(int,V),()).

%%%%%%%%%%%%%%%%% comparison equality
operator_declare(OP,(T,(T,())),bool) :- T = int, OP = (eq;neq;leq;lt;geq;gt).
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=eq,  ARGS = (val(int,V1),(val(int,V2),())), V1 =  V2.
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=neq, ARGS = (val(int,V1),(val(int,V2),())), V1 != V2.
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=leq, ARGS = (val(int,V1),(val(int,V2),())), V1 <= V2.
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=lt,  ARGS = (val(int,V1),(val(int,V2),())), V1 <  V2.
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=geq, ARGS = (val(int,V1),(val(int,V2),())), V1 >= V2.
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=gt,  ARGS = (val(int,V1),(val(int,V2),())), V1 >  V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=eq,  ARGS = (val(int,V1),(val(int,V2),())), V1 != V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=neq, ARGS = (val(int,V1),(val(int,V2),())), V1 =  V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=leq, ARGS = (val(int,V1),(val(int,V2),())), V1 >  V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=lt,  ARGS = (val(int,V1),(val(int,V2),())), V1 >= V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=geq, ARGS = (val(int,V1),(val(int,V2),())), V1 <  V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=gt,  ARGS = (val(int,V1),(val(int,V2),())), V1 <= V2.

_computed(OP,ARGS,RES) :- _compute(OP,ARGS), OP=float_div, ARGS = (val(int,_),(val(int,V2),())), V2!=0,
  RES = @pythonEvalExpr(operation(OP,ARGS),(),ID),
  _main_solverIdentifier(ID).
