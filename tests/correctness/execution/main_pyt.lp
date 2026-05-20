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
