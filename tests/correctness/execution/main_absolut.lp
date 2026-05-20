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
