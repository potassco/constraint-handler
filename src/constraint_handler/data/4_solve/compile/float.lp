_expression_pythonEval(E,operation(OP,(val(int,V),()))) :- _computeIdx(E,OP), intToFloatOperator(OP), _computeIdx(E,0,val(int,V)).
_expression_pythonEval(E,operation(OP,(val(float,V),()))) :- _computeIdx(E,OP), floatUnOperator(OP), _computeIdx(E,0,val(float,V)).
_expression_pythonEval(E,operation(OP,(val(T1,V1),(val(T2,V2),())))) :- _computeIdx(E,OP), floatBinOperator(OP), _computeIdx(E,0,val(T1,V1)), _computeIdx(E,1,val(T2,V2)),
    (T1;T2)=float, T1=(float;int), T2=(float;int).
_expression_pythonEval(E,operation(OP,(val(T1,V1),(val(T2,V2),())))) :- _computeIdx(E,OP), OP=(eq;neq), _computeIdx(E,0,val(T1,V1)), _computeIdx(E,1,val(T2,V2)),
    T1=(float;int), T2=(float;int), T1 != T2.

_computedIdx(E,val(bool,true)) :- _computeIdx(E,eq), _computeIdx(E,0,val(float,V)), _computeIdx(E,1,val(float,V)).
_computedIdx(E,val(bool,false)) :- _computeIdx(E,eq), _computeIdx(E,0,val(float,_)), _computeIdx(E,1,val(float,V)), not _computeIdx(E,0,val(float,V)).
_computedIdx(E,val(bool,false)) :- _computeIdx(E,eq), _computeIdx(E,0,val(float,V)), _computeIdx(E,1,val(float,_)), not _computeIdx(E,1,val(float,V)).
_computedIdx(E,val(bool,false)) :- _computeIdx(E,neq), _computeIdx(E,0,val(float,V)), _computeIdx(E,1,val(float,V)).
_computedIdx(E,val(bool,true)) :- _computeIdx(E,neq), _computeIdx(E,0,val(float,_)), _computeIdx(E,1,val(float,V)), not _computeIdx(E,0,val(float,V)).
_computedIdx(E,val(bool,true)) :- _computeIdx(E,neq), _computeIdx(E,0,val(float,V)), _computeIdx(E,1,val(float,_)), not _computeIdx(E,1,val(float,V)).
