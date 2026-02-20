%% snippet(input: x, output: y):
%%     if x is not None and x = False:
%%         y := 5
execution_declare(dummy,snippet,STMT,(x,()),(y,())) :-
    COND = operation(hasValue,(variable(x),())),
    XFAL = operation(eq,(variable(x),(val(bool,false),()))),
    EXPR = operation(conj,(COND,(XFAL,()))),
    STMT = if(EXPR,assign(y,val(int,5)),noop).

variable_declare(dummy,execution_input(snippet,x),fromFacts).
variable_domain(execution_input(snippet,x),val(bool,(true;false))).
variable_domain(execution_input(snippet,x),val(none,none)).

execution_run(dummy,snippet).

evaluate(leqv,
  (operation(eq,(variable(execution_output(snippet,y)),(val(int,5),()))),
  (operation(eq,(variable(execution_input(snippet,x)),(val(bool,false),()))),()))).

#show value/2.
#show evaluated/3.
