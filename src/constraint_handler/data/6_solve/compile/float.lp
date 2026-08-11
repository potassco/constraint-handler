%%%%%%%%%%%%%%%%% add
_computedIdx(operation(add,(ARG,())),val(float,V)) :-
    _expression(compile,operation(add,(ARG,()))),
    _se_value(ARG,val(float,V)).

_direct_resortToPython(operation(add,(ARG1,(ARG2,REST)))) :-
    _expression(compile,operation(add,(ARG1,(ARG2,REST)))),
    _computeIdx(operation(add,(ARG1,(ARG2,REST))),IDX,val(float,V)).


%%%%%%%%%%%%%%%%% mult
_computedIdx(operation(mult,(ARG,())),val(float,V)) :-
    _expression(compile,operation(mult,(ARG,()))),
    _se_value(ARG,val(float,V)).

_direct_resortToPython(operation(mult,(ARG1,(ARG2,REST)))) :-
    _expression(compile,operation(mult,(ARG1,(ARG2,REST)))),
    _computeIdx(operation(mult,(ARG1,(ARG2,REST))),IDX,val(float,V)).

_operator_forFloat(abs;acos;asin;atan;ceil;cos;floor;minus;sin;sqrt;tan).
_operator_forFloat(float_div;int_div;float_div;geq;gt;leq;lt;max;min;pow;sub).
_operator_needsPython(OP,float) :- operator_declare(OP,(float,()),T), _operator_forFloat(OP).
_operator_needsPython(OP,int) :- operator_declare(OP,(int,()),float), _operator_forFloat(OP).
_operator_needsPython(OP,T1,T2) :- operator_declare(OP,(T1,(T2,())),T), (T1;T2)=float, _operator_forFloat(OP).
_operator_needsPython(OP,T1,T2) :- (T1,T2)=((float,int);(int,float)), OP=(eq;neq).
_operator_needsPython(float_div,int,int).

_expression_pythonEval(E,operation(OP,(val(T,V),()))) :- _computeIdx(E,OP), _operator_needsPython(OP,T), _computeIdx(E,0,val(T,V)).
_expression_pythonEval(E,operation(OP,(val(T1,V1),(val(T2,V2),())))) :- _computeIdx(E,OP), _operator_needsPython(OP,T1,T2), _computeIdx(E,0,val(T1,V1)), _computeIdx(E,1,val(T2,V2)).

_computedIdx(E,val(bool,true)) :- _computeIdx(E,eq), _computeIdx(E,0,val(float,V)), _computeIdx(E,1,val(float,V)).
_computedIdx(E,val(bool,false)) :- _computeIdx(E,eq), _computeIdx(E,0,val(float,_)), _computeIdx(E,1,val(float,V)), not _computeIdx(E,0,val(float,V)).
_computedIdx(E,val(bool,false)) :- _computeIdx(E,eq), _computeIdx(E,0,val(float,V)), _computeIdx(E,1,val(float,_)), not _computeIdx(E,1,val(float,V)).
_computedIdx(E,val(bool,false)) :- _computeIdx(E,neq), _computeIdx(E,0,val(float,V)), _computeIdx(E,1,val(float,V)).
_computedIdx(E,val(bool,true)) :- _computeIdx(E,neq), _computeIdx(E,0,val(float,_)), _computeIdx(E,1,val(float,V)), not _computeIdx(E,0,val(float,V)).
_computedIdx(E,val(bool,true)) :- _computeIdx(E,neq), _computeIdx(E,0,val(float,V)), _computeIdx(E,1,val(float,_)), not _computeIdx(E,1,val(float,V)).

_computedIdx(E,bad) :- _computeIdx(E,(lt;leq;geq;gt)), _computeIdx(E,0,val(T0,V0)), _computeIdx(E,1,val(T1,V1)),
    (T0;T1)=(float;int), OT=(T0;T1), OT!=float, OT!=int.

_computedIdx(E,val(bool,RESULT)) :- _computeIdx(E,OP), _computeIdx(E,0,val(T0,V0)), _computeIdx(E,1,val(T1,V1)),
    (OP,RESULT)=((eq,false);(neq,true)),
    (T0;T1)=(float;int), OT=(T0;T1), OT!=float, OT!=int.
