intToFloatOperator(sqrt;cos;sin;tan;acos;asin;atan).
floatUnOperator(abs;sqrt;cos;sin;tan;acos;asin;atan;minus;floor).
floatBinOperator(add;sub;mult;int_div;float_div;pow;leq;lt;geq;gt;max;min).

operator_declare_variadic(OP,T,T,2) :- T = float, OP = (add;mult).
operator_declare(OP,(T,()),float) :- T = (int;float), intToFloatOperator(OP).
operator_declare(OP,(T,()),float) :- T = float, OP = (abs;minus).
operator_declare(OP,(T,()),int) :- T = float, OP = floor.
operator_declare(OP,(T1,(T2,())),float) :- T1 = (int;float),T2 = (int;float), (T1,T2) != (int,int), floatBinOperator(OP).
operator_declare(OP,(T,(T,())),float) :- T = int, OP = float_div.
operator_declare(OP,(T1,(T2,())),bool) :- T1 = (int;float),T2 = (int;float), (T1,T2) != (int,int), OP = (leq;lt;geq;gt).
operator_declare(OP,(T,(T,())),bool) :- T = float, OP = (eq;neq).

_stageCompute(OP,ARGS,L) :- _compute(OP,ARGS), intToFloatOperator(OP), ARGS = (val(int,V),()), L=(V,()).
_stageCompute(OP,ARGS,L) :- _compute(OP,ARGS), floatUnOperator(OP), ARGS=(val(float,V),()), L=(V,()).
_stageCompute(OP,ARGS,L) :- _compute(OP,ARGS), floatBinOperator(OP), ARGS=(val(T1,V1),(val(T2,V2),())), L=(V1,(V2,())),
    (T1;T2)=float, T1=(float;int), T2=(float;int).
_stageCompute(OP,ARGS,L) :- _compute(OP,ARGS), OP=(eq;neq), ARGS=(val(T1,V1),(val(T2,V2),())), L=(V1,(V2,())),
    T1=float, T2=float.

_expression_eval_exec(OP,ARGS,RES) :- _stageCompute(OP,ARGS,L), RES = @pythonEvalExpr(operation(OP,ARGS),(),ID), _main_solverIdentifier(ID).
_computed(OP,ARGS,val(TYPE,V)) :- _expression_eval_exec(OP,ARGS,val(TYPE,V)).
_warning(KIND,(),(OP,ARGS,MSG)) :- _expression_eval_exec(OP,ARGS,error(KIND,MSG)).
