intToFloatOperator(sqrt;cos;sin;tan;acos;asin;atan).
floatUnOperator(abs;sqrt;cos;sin;tan;acos;asin;atan;minus;floor).
floatBinOperator(add;sub;mult;div;fdiv;pow;leq;lt;geq;gt).

stageCompute(OP,ARGS,L) :- compute(OP,ARGS), intToFloatOperator(OP), ARGS = (val(int,V),()), L=(V,()).
stageCompute(OP,ARGS,L) :- compute(OP,ARGS), floatUnOperator(OP), ARGS=(val(float,V),()), L=(V,()).
stageCompute(OP,ARGS,L) :- compute(OP,ARGS), floatBinOperator(OP), ARGS=(val(T1,V1),(val(T2,V2),())), L=(V1,(V2,())),
    (T1;T2)=float, T1=(float;int), T2=(float;int).
stageCompute(OP,ARGS,L) :- compute(OP,ARGS), OP=(eq;neq), ARGS=(val(T1,V1),(val(T2,V2),())), L=(V1,(V2,())),
    T1=float, T2=float.

computed(OP,ARGS,val(T,RES)) :- stageCompute(OP,ARGS,L), (T,RES) = @pythonEvalOperator(OP,L).
