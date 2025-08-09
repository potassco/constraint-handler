intToFloatOperator(sqrt;cos;sin;tan;acos;asin;atan).
floatUnOperator(abs;sqrt;cos;sin;tan;acos;asin;atan;minus;floor).
floatBinOperator(add;sub;mult;div;pow;leq;lt;geq;gt).

stageCompute(OP,ARGS,L) :- compute(OP,ARGS), intToFloatOperator(OP), ARGS = (int,(V,())), L=(V,()).
stageCompute(OP,ARGS,L) :- compute(OP,ARGS), floatUnOperator(OP), ARGS=(float,(V,())), L=(V,()).
stageCompute(OP,ARGS,L) :- compute(OP,ARGS), floatBinOperator(OP), ARGS=(T1,(V1,(T2,(V2,())))), L=(V1,(V2,())),
    (T1;T2)=float, T1=(float;int), T2=(float;int).
stagePCompute(OP,S,ARGS) :- compute(OP,ARGS), OP=python(E), eValue(E,str,S).

computed(OP,ARGS,T,RES) :- stageCompute(OP,ARGS,L), (T,RES) = @pythonEvalOperator(OP,L).
computed(OP,ARGS,T,RES) :- stagePCompute(OP,S,ARGS), L=@pythonMergeTypes(ARGS), (T,RES) = @pythonEvalOperator(S,L).

computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=eq,  ARGS = (float,(V1,(float,(V2,())))), V1 =  V2.
computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=neq, ARGS = (float,(V1,(float,(V2,())))), V1 != V2.
computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=eq,  ARGS = (float,(V1,(float,(V2,())))), V1 != V2.
computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=neq, ARGS = (float,(V1,(float,(V2,())))), V1 =  V2.
