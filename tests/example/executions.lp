#include "includeAll.lp".
#show warning/1.
#show value/3.



%% absolut(input: x, output: y):
%%     if x >=0:
%%         y := x
%%     else:
%%         y := x*(-1)
exec_declare(dummy,absolut,STMT,(x,()),(y,())) :-
    GEQ  = operation(geq,(variable(x),(val(int,0),()))),
    THEN = assign(y,variable(x)),
    ELSE = assign(y,operation(mult,(variable(x),(val(int,-1),())))),
    STMT = if(GEQ,THEN,ELSE).
1 { assign(dummy,exec_input(absolut,x),val(int,(-2;0;2))) } 1.
exec_run(dummy,absolut).






%% swap(input: x,y, output: x,y, internal: tmp):
%%     tmp := x
%%     x := y
%%     y := tmp
exec_declare(dummy,swap,STMT,VARS,VARS) :-
    STMT1 = assign(tmp,variable(x)),
    STMT2 = assign(x,variable(y)),
    STMT3 = assign(y,variable(tmp)),
    STMT  = seq2(STMT1,seq2(STMT2,STMT3)),
    VARS  = (x,(y,())).

%1 { assign(dummy,exec_input(swap,x),val(int,(10;20))) } 1.
1 { assign(dummy,exec_input(swap,y),val(int,(30;40))) } 1.
exec_run(dummy,swap).

1 { assign(dummy,start,val(int,(10;20))) } 1.
assign(dummy,exec_input(swap,x),variable(start)).
assign(dummy,theend,variable(exec_output(swap,x))).

ensure(dummy,operation(eq,(variable(theend),(val(int,40),())))).





%% factorial(input: n, output: f):
%%     f := 1
%%     while n >=1:
%%         f := n*f
%%         n := n-1
exec_declare(dummy,factorial,STMT,(n,()),(f,())) :-
    GEQ  = operation(geq,(variable(n),(val(int,1),()))),
    INIT = assign(f,val(int,1)),
    MULT = assign(f,operation(mult,(variable(n),(variable(f),())))),
    DECR = assign(n,operation(sub,(variable(n),(val(int,1),())))),
    BODY = seq2(MULT,DECR),
    LOOP = while(10,GEQ,BODY),    %%%% CHEATING
    STMT = seq2(INIT,LOOP).
assign(dummy,exec_input(factorial,n),val(int,5)).
exec_run(dummy,factorial).






%% pyt(input: "x", output: "x",y, internal: z):
%%     z := 1+"x"
%%     python.exec(x = x+1, globals=dict(), locals={ "x": valueOf("x") })
%%     "x" := locals["x"]
%%     y := z + "x"
exec_declare(dummy,pyt,STMT,("x",()),("x",(y,()))) :-
    STMT1 = assign(z,operation(add,(val(int,1),(variable("x"),())))),
    STMT2 = python("x = x+1",("x",()),("x",())),
    STMT3 = assign(y,operation(add,(variable(z),(variable("x"),())))),
    STMT  = seq2(STMT1,seq2(STMT2,STMT3)).
1 { assign(dummy,exec_input(pyt,"x"),val(int,(10;20))) } 1.
exec_run(dummy,pyt).


