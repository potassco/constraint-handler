%% absolut(input: x, output: y):
%%     if x >=0:
%%         y := x
%%     else:
%%         y := x*(-1)
execution_declare(absolut,STMT,(x,()),(y,())) :-
    GEQ  = operation(geq,(variable(x),(val(int,0),()))),
    THEN = assign(y,variable(x)),
    ELSE = assign(y,operation(mult,(variable(x),(val(int,-1),())))),
    STMT = if(GEQ,THEN,ELSE).
variable_declare(execution_input(absolut,x),fromFacts).
variable_domain(execution_input(absolut,x),val(int,(-2;0;2))).
execution_run(absolut).
evaluate(geq,(variable(execution_output(absolut,y)),(val(int,0),()))).
evaluate(eq,
        (operation(mult,
                  (variable(execution_output(absolut,y)),
                  (variable(execution_output(absolut,y)),()))),
        (operation(mult,
                  (variable(execution_input(absolut,x)),
                  (variable(execution_input(absolut,x)),()))),()))).





%% swap(input: x,y, output: x,y, internal: tmp):
%%     tmp := x
%%     x := y
%%     y := tmp
execution_declare(swap,STMT,VARS,VARS) :-
    STMT1 = assign(tmp,variable(x)),
    STMT2 = assign(x,variable(y)),
    STMT3 = assign(y,variable(tmp)),
    STMT  = seq2(STMT1,seq2(STMT2,STMT3)),
    VARS  = (x,(y,())).

variable_declare(execution_input(swap,x),fromFacts).
variable_domain(execution_input(swap,x),val(int,(10;20))).
variable_declare(execution_input(swap,y),fromFacts).
variable_domain(execution_input(swap,y),val(int,(30;40))).
execution_run(swap).
evaluate(eq,(variable(execution_output(swap,x)),(variable(execution_input(swap,y)),()))).
evaluate(eq,(variable(execution_output(swap,y)),(variable(execution_input(swap,x)),()))).



%% pyt(input: "x", output: "x",y, internal: z):
%%     z := 1+"x"
%%     python.exec(x = x+1, globals=dict(), locals={ "x": valueOf("x") })
%%     "x" := locals["x"]
%%     y := z + "x"
execution_declare(pyt,STMT,("x",()),("x",(y,()))) :-
    STMT1 = assign(z,operation(add,(val(int,1),(variable("x"),())))),
    STMT2 = statement_python("x = x+1"),
    STMT3 = assign(y,operation(add,(variable(z),(variable("x"),())))),
    STMT  = seq2(STMT1,seq2(STMT2,STMT3)).
variable_define(execution_input(pyt,"x"),val(int,10)).
execution_run(pyt).
