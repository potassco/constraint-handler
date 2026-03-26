intToFloatOperator(sqrt;cos;sin;tan;acos;asin;atan).
floatUnOperator(abs;sqrt;cos;sin;tan;acos;asin;atan;minus;floor).
floatFloatFloatOperator(add;sub;mult;float_div;pow;max;min).
floatBinOperator(OP) :- floatFloatFloatOperator(OP).
floatBinOperator(int_div;leq;lt;geq;gt).

operator_declare_variadic(OP,T,T,2) :- T = float, OP = (add;mult).
operator_declare(OP,(T,()),float) :- T = (int;float), intToFloatOperator(OP).
operator_declare(OP,(T,()),float) :- T = float, OP = (abs;minus).
operator_declare(OP,(T,()),int) :- T = float, OP = floor.
operator_declare(OP,(T1,(T2,())),float) :- T1 = (int;float),T2 = (int;float), (T1,T2) != (int,int), floatFloatFloatOperator(OP).
operator_declare(OP,(T,(T,())),float) :- T = int, OP = float_div.
operator_declare(OP,(T1,(T2,())),bool) :- T1 = (int;float),T2 = (int;float), (T1,T2) != (int,int), OP = (leq;lt;geq;gt).
operator_declare(OP,(T,(T,())),bool) :- T = float, OP = (eq;neq).

_float_stageCompute(E,ER) :- _computeIdx(E,OP), intToFloatOperator(OP), _computeIdx(E,0,val(int,V)), ER=operation(OP,(val(int,V),())).
_float_stageCompute(E,ER) :- _computeIdx(E,OP), floatUnOperator(OP), _computeIdx(E,0,val(float,V)), ER=operation(OP,(val(float,V),())).
_float_stageCompute(E,ER) :- _computeIdx(E,OP), floatBinOperator(OP), _computeIdx(E,0,val(T1,V1)), _computeIdx(E,1,val(T2,V2)),
    (T1;T2)=float, T1=(float;int), T2=(float;int),
  ER=operation(OP,(val(T1,V1),(val(T2,V2),()))).
%_float_stageCompute(E,ER) :- _computeIdx(E,OP), OP=(eq;neq), _computeIdx(E,0,val(float,V1)), _computeIdx(E,1,val(float,V2)),
%  ER=operation(OP,(val(float,V1),(val(float,V2),()))).

_float_stageComputed(E,RES) :- _float_stageCompute(E,ER), RES = @pythonEvalExpr(ER,(),ID), _main_solverIdentifier(ID).
_computedIdx(E,val(T,V)) :- _float_stageComputed(E,val(T,V)).
_computedIdx(E,bad) :- _float_stageComputed(E,error(_,_)).
_warning(KIND,(),(E,MSG)) :- _float_stageComputed(E,error(KIND,MSG)).

_stageCompute(OP,ARGS) :- _compute(OP,ARGS), OP=(eq;neq), ARGS=(val(T1,V1),(val(T2,V2),())),
    T1=float, T2=float.
_expression_eval_exec(OP,ARGS,RES) :- _stageCompute(OP,ARGS), RES = @pythonEvalExpr(operation(OP,ARGS),(),ID), _main_solverIdentifier(ID).
_computed(OP,ARGS,val(TYPE,V)) :- _expression_eval_exec(OP,ARGS,val(TYPE,V)).
_warning(KIND,(),(OP,ARGS,MSG)) :- _expression_eval_exec(OP,ARGS,error(KIND,MSG)).