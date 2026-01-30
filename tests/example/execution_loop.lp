%% factorial(input: n, output: f):
%%     f := 1
%%     while n >=1:
%%         f := n*f
%%         n := n-1
execution_declare(dummy,factorial,STMT,(n,()),(f,())) :-
    GEQ  = operation(geq,(variable(n),(val(int,1),()))),
    INIT = assign(f,val(int,1)),
    MULT = assign(f,operation(mult,(variable(n),(variable(f),())))),
    DECR = assign(n,operation(sub,(variable(n),(val(int,1),())))),
    BODY = seq2(MULT,DECR),
    LOOP = while(8,GEQ,BODY),    %%%% CHEATING
    STMT = seq2(INIT,LOOP).
variable_declare(dummy,execution_input(factorial,n),fromFacts).
variable_domain (execution_input(factorial,n),val(int,(3;5))).
execution_run(dummy,factorial).
