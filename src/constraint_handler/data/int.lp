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

%%%%%%%%%%%%%%%%% sub pow
operator_declare(OP,(T,(T,())),T) :- T = int, OP = (sub;pow).
_computedIdx(E,val(int,V0-V1))  :- _computeIdx(E,sub), _computeIdx(E,0,val(int,V0)), _computeIdx(E,1,val(int,V1)).
_computedIdx(E,val(int,V0**V1)) :- _computeIdx(E,pow), _computeIdx(E,0,val(int,V0)), _computeIdx(E,1,val(int,V1)).

%%%%%%%%%%%%%%%%% int_div
operator_declare(OP,(T1,(T2,())),T) :- T = int, T1 = (int;float), T2 = (int;float), OP = int_div.
_computedIdx(E,val(int,V0/V1)) :- _computeIdx(E,int_div), _computeIdx(E,0,val(int,V0)), _computeIdx(E,1,val(int,V1)), V1 != 0.
_computedIdx(E,bad) :- _computeIdx(E,(int_div;float_div)), _computeIdx(E,1,val(int,0)).
warning(expression(zeroDivisionError),(),(OP,E)) :- _computeIdx(E,OP), OP = (int_div;float_div), _computeIdx(E,1,val(int,0)).


%%%%%%%%%%%%%%%%% abs minus
operator_declare(OP,(T,()),T) :- T = int, OP = (abs;minus).
_computedIdx(E,val(int,|V|)) :- _computeIdx(E,abs), _computeIdx(E,0,val(int,V)).
_computedIdx(E,val(int,-V))  :- _computeIdx(E,minus), _computeIdx(E,0,val(int,V)).

%%%%%%%%%%%%%%%%% equality
operator_declare(OP,(T,(T,())),bool) :- T = int, OP = (eq;neq).
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=eq,  ARGS = (val(int,V1),(val(int,V2),())), V1 =  V2.
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=neq, ARGS = (val(int,V1),(val(int,V2),())), V1 != V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=eq,  ARGS = (val(int,V1),(val(int,V2),())), V1 != V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=neq, ARGS = (val(int,V1),(val(int,V2),())), V1 =  V2.

%%%%%%%%%%%%%%%%% comparison
operator_declare(OP,(T,(T,())),bool) :- T = int, OP = (leq;lt;geq;gt).
_computedIdx(E,val(bool,true)) :- _computeIdx(E,leq), _computeIdx(E,0,val(int,V1)), _computeIdx(E,1,val(int,V2)), V1 <= V2.
_computedIdx(E,val(bool,true)) :- _computeIdx(E,lt),  _computeIdx(E,0,val(int,V1)), _computeIdx(E,1,val(int,V2)), V1 < V2.
_computedIdx(E,val(bool,true)) :- _computeIdx(E,geq), _computeIdx(E,0,val(int,V1)), _computeIdx(E,1,val(int,V2)), V1 >= V2.
_computedIdx(E,val(bool,true)) :- _computeIdx(E,gt),  _computeIdx(E,0,val(int,V1)), _computeIdx(E,1,val(int,V2)), V1 > V2.

_computedIdx(E,val(bool,false)) :- _computeIdx(E,leq), _computeIdx(E,0,val(int,V1)), _computeIdx(E,1,val(int,V2)), V1 > V2.
_computedIdx(E,val(bool,false)) :- _computeIdx(E,lt),  _computeIdx(E,0,val(int,V1)), _computeIdx(E,1,val(int,V2)), V1 >= V2.
_computedIdx(E,val(bool,false)) :- _computeIdx(E,geq), _computeIdx(E,0,val(int,V1)), _computeIdx(E,1,val(int,V2)), V1 < V2.
_computedIdx(E,val(bool,false)) :- _computeIdx(E,gt),  _computeIdx(E,0,val(int,V1)), _computeIdx(E,1,val(int,V2)), V1 <= V2.

_computedIdx(E,val(int,V2)) :- _computeIdx(E,max), _computeIdx(E,0,val(int,V1)), _computeIdx(E,1,val(int,V2)), V1 <= V2.
_computedIdx(E,val(int,V1)) :- _computeIdx(E,max), _computeIdx(E,0,val(int,V1)), _computeIdx(E,1,val(int,V2)), V1 > V2.
_computedIdx(E,val(int,V2)) :- _computeIdx(E,min), _computeIdx(E,0,val(int,V1)), _computeIdx(E,1,val(int,V2)), V1 > V2.
_computedIdx(E,val(int,V1)) :- _computeIdx(E,min), _computeIdx(E,0,val(int,V1)), _computeIdx(E,1,val(int,V2)), V1 <= V2.

_computed(OP,ARGS,RES) :- _compute(OP,ARGS), OP=float_div, ARGS = (val(int,_),(val(int,V2),())), V2!=0,
  RES = @pythonEvalExpr(operation(OP,ARGS),(),ID),
  _main_solverIdentifier(ID).
