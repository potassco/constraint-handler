%%%%%%%%%%%%%%%%% add mult
operator_declare_variadic((add;mult),int,int,1).
_int_add(E,0,val(int,0)) :- _computeIdx(E,add).
_int_add(E,IDX+1,val(int,VO+V)) :- _computeIdx(E,add), _computeIdx(E,IDX,val(int,V)), _int_add(E,IDX,val(int,VO)).
_computedIdx(E,V)  :- _computeIdx(E,add), _int_add(E,IDX,V), not _computeIdx(E,IDX,_). % TODO: avoid negation

% short circuit if there is a 0
_computedIdx(E,val(int,0)) :- _computeIdx(E,mult), _computeIdx(E,IDX,val(int,0)).
_int_mult(E,0,val(int,1)) :- _computeIdx(E,mult).
_int_mult(E,IDX+1,val(int,VO*V)) :- _computeIdx(E,mult), _computeIdx(E,IDX,val(int,V)), _int_mult(E,IDX,val(int,VO)).
_computedIdx(E,V)  :- _computeIdx(E,mult), _int_mult(E,IDX,V), not _computeIdx(E,IDX,_).

%%%%%%%%%%%%%%%%% sub pow
operator_declare((sub;pow),(int,(int,())),int).
_computedIdx(E,val(int,V0-V1))  :- _computeIdx(E,sub), _computeIdx(E,0,val(int,V0)), _computeIdx(E,1,val(int,V1)).
_computedIdx(E,val(int,V0**V1)) :- _computeIdx(E,pow), _computeIdx(E,0,val(int,V0)), _computeIdx(E,1,val(int,V1)).
_computedIdx(E,val(int,1))      :- _computeIdx(E,pow), _computeIdx(E,0,_), _computeIdx(E,1,val(int,0)).
_computedIdx(E,bad)             :- _computeIdx(E,pow), _computeIdx(E,0,bad), _computeIdx(E,1,val(int,V1)), V1 != 0.
_computedIdx(E,bad)             :- _computeIdx(E,pow), _computeIdx(E,0,_), _computeIdx(E,1,bad).

%%%%%%%%%%%%%%%%% int_div
operator_declare(int_div,((int;float),((int;float),())),int).
_computedIdx(E,val(int,V0/V1)) :- _computeIdx(E,int_div), _computeIdx(E,0,val(int,V0)), _computeIdx(E,1,val(int,V1)), V1 != 0.
_computedIdx(E,bad) :- _computeIdx(E,(int_div;float_div)), _computeIdx(E,1,val(int,0)).
warning(expression(zeroDivisionError),(),(OP,E)) :- _computeIdx(E,OP), OP = (int_div;float_div), _computeIdx(E,1,val(int,0)).


%%%%%%%%%%%%%%%%% abs minus
operator_declare((abs;minus),(int,()),int).
_computedIdx(E,val(int,|V|)) :- _computeIdx(E,abs), _computeIdx(E,0,val(int,V)).
_computedIdx(E,val(int,-V))  :- _computeIdx(E,minus), _computeIdx(E,0,val(int,V)).

%%%%%%%%%%%%%%%%% eq neq
_type_extensionalEquality(int).

%%%%%%%%%%%%%%%%% leq lt geq gt
_type_extensionalOrder(int).

%%%%%%%%%%%%%%%%% max min
_computedIdx(E,val(int,V2)) :- _computeIdx(E,max), _computeIdx(E,0,val(int,V1)), _computeIdx(E,1,val(int,V2)), V1 <= V2.
_computedIdx(E,val(int,V1)) :- _computeIdx(E,max), _computeIdx(E,0,val(int,V1)), _computeIdx(E,1,val(int,V2)), V1 > V2.
_computedIdx(E,val(int,V2)) :- _computeIdx(E,min), _computeIdx(E,0,val(int,V1)), _computeIdx(E,1,val(int,V2)), V1 > V2.
_computedIdx(E,val(int,V1)) :- _computeIdx(E,min), _computeIdx(E,0,val(int,V1)), _computeIdx(E,1,val(int,V2)), V1 <= V2.

_expression_pythonEval(E,operation(float_div,(val(int,V1),(val(int,V2),())))) :- _computeIdx(E,float_div), _computeIdx(E,0,val(int,V1)), _computeIdx(E,1,val(int,V2)).
