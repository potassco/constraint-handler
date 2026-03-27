intToFloatOperator(sqrt;cos;sin;tan;acos;asin;atan).
floatUnOperator(abs;sqrt;cos;sin;tan;acos;asin;atan;minus;floor).
floatFloatFloatOperator(add;sub;mult;float_div;pow;max;min).
floatBinOperator(OP) :- floatFloatFloatOperator(OP).
floatBinOperator(int_div;leq;lt;geq;gt).

operator_declare_variadic((add;mult),float,float,2).
operator_declare(OP,((int;float),()),float) :- intToFloatOperator(OP).
operator_declare((abs;minus),(float,()),float).
operator_declare(floor,(float,()),int).
operator_declare(OP,(T1,(T2,())),float) :- T1 = (int;float),T2 = (int;float), (T1,T2) != (int,int), floatFloatFloatOperator(OP).
operator_declare(float_div,(int,(int,())),float).
operator_declare((leq;lt;geq;gt),(T1,(T2,())),bool) :- T1 = (int;float),T2 = (int;float), (T1,T2) != (int,int).
operator_declare((eq;neq),(float,(float,())),bool).

_expression_pythonEval(E,operation(OP,(val(int,V),()))) :- _computeIdx(E,OP), intToFloatOperator(OP), _computeIdx(E,0,val(int,V)).
_expression_pythonEval(E,operation(OP,(val(float,V),()))) :- _computeIdx(E,OP), floatUnOperator(OP), _computeIdx(E,0,val(float,V)).
_expression_pythonEval(E,operation(OP,(val(T1,V1),(val(T2,V2),())))) :- _computeIdx(E,OP), floatBinOperator(OP), _computeIdx(E,0,val(T1,V1)), _computeIdx(E,1,val(T2,V2)),
    (T1;T2)=float, T1=(float;int), T2=(float;int).
_expression_pythonEval(E,operation(OP,(val(float,V1),(val(float,V2),())))) :- _computeIdx(E,OP), OP=(eq;neq), _computeIdx(E,0,val(float,V1)), _computeIdx(E,1,val(float,V2)).