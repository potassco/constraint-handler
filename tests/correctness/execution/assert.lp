variable_declare(gx,fromFacts).
variable_domain(gx,val(int,1..3)).
variable_declare(gy,fromFacts).
variable_domain(gy,val(int,1..3)).

%% myfun(input: x,y, output: z):
%%     assert x != y
%%     z := x+y
execution_declare(myfun,STMT,(x,(y,())),(z,())) :-
    NEQ  = operation(neq,(variable(x),(variable(y),()))),
    SUM  = operation(add,(variable(x),(variable(y),()))),
    STMT = seq2(assert(NEQ),assign(z,SUM)).
    %STMT = seq2(assign(w,NEQ),assign(z,SUM)).
execution_run(myfun).

variable_define(execution_input(myfun,x),variable(gx)).
variable_define(execution_input(myfun,y),variable(gy)).
variable_define(gz,variable(execution_output(myfun,z))).

variable_define(same,operation(eq,(variable(gx),(variable(gy),())))).

evaluate(neq,(variable(gx),(variable(gy),()))).
