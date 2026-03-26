%%%%%%%%%%%%%%%%% add mult
operator_declare_variadic((add;mult),int,int,1).
_computed(add,(),val(int,0)) :- _compute(add,()).
_compute(add,TAIL) :- _compute(add,(val(int,_),TAIL)).
_computed(add,(val(int,V1),TAIL),val(int,V1+VTAIL)) :-
    _compute(add,(val(int,V1),TAIL)),
    _computed(add,TAIL,val(int,VTAIL)).

% short circuit if there is a 0
_computedIdx(E,val(int,0)) :- _computeIdx(E,mult), _computeIdx(E,IDX,val(int,0)).
_computedIdx(E,val(int,1)) :- _computeIdx(E,mult), not _computeIdx(E, 0, _).
_int_mult(E,0,val(int,1)) :- _computeIdx(E,mult).
_int_mult(E,IDX+1,val(int,VO*V)) :- _computeIdx(E,mult), _computeIdx(E,IDX,val(int,V)), _int_mult(E,IDX,val(int,VO)).
_computedIdx(E,V)  :- _computeIdx(E,mult), _int_mult(E,IDX,V),_computeIdx(E,IDX-1,_), not _computeIdx(E,IDX,_).

%%%%%%%%%%%%%%%%% sub pow
operator_declare((sub;pow),(int,(int,())),int).
_computedIdx(E,val(int,V0-V1))  :- _computeIdx(E,sub), _computeIdx(E,0,val(int,V0)), _computeIdx(E,1,val(int,V1)).
_computedIdx(E,val(int,V0**V1)) :- _computeIdx(E,pow), _computeIdx(E,0,val(int,V0)), _computeIdx(E,1,val(int,V1)).

%%%%%%%%%%%%%%%%% int_div
operator_declare(int_div,((int;float),((int;float),())),int).
_computedIdx(E,val(int,V0/V1)) :- _computeIdx(E,int_div), _computeIdx(E,0,val(int,V0)), _computeIdx(E,1,val(int,V1)), V1 != 0.
_computedIdx(E,bad) :- _computeIdx(E,(int_div;float_div)), _computeIdx(E,1,val(int,0)).
warning(expression(zeroDivisionError),(),(OP,E)) :- _computeIdx(E,OP), OP = (int_div;float_div), _computeIdx(E,1,val(int,0)).


%%%%%%%%%%%%%%%%% abs minus
operator_declare((abs;minus),(int,()),int).
_computedIdx(E,val(int,|V|)) :- _computeIdx(E,abs), _computeIdx(E,0,val(int,V)).
_computedIdx(E,val(int,-V))  :- _computeIdx(E,minus), _computeIdx(E,0,val(int,V)).

%%%%%%%%%%%%%%%%% equality
operator_declare((eq;neq),(int,(int,())),bool).
_computed(eq, (val(int,V1),(val(int,V2),())),val(bool,true))  :- _compute(eq, (val(int,V1),(val(int,V2),()))), V1 =  V2.
_computed(neq,(val(int,V1),(val(int,V2),())),val(bool,true))  :- _compute(neq,(val(int,V1),(val(int,V2),()))), V1 != V2.
_computed(eq, (val(int,V1),(val(int,V2),())),val(bool,false)) :- _compute(eq, (val(int,V1),(val(int,V2),()))), V1 != V2.
_computed(neq,(val(int,V1),(val(int,V2),())),val(bool,false)) :- _compute(neq,(val(int,V1),(val(int,V2),()))), V1 =  V2.

%%%%%%%%%%%%%%%%% comparison
operator_declare((leq;lt;geq;gt),(int,(int,())),bool).
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

_computed(float_div,(val(int,V1),(val(int,V2),())),RES) :- _compute(float_div,(val(int,V1),(val(int,V2),()))), V2!=0,
  RES=@pythonEvalExpr(operation(float_div,(val(int,V1),(val(int,V2),()))),(),ID),
  _main_solverIdentifier(ID).
