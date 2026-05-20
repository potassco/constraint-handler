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
