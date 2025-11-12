#include "includeAll.lp".

1 { assign(dummy,gx,val(int,1..3)) } 1.
1 { assign(dummy,gy,val(int,1..3)) } 1.

%% myfun(input: x,y, output: z):
%%     assert x != y
%%     z := x+y
execution_declare(dummy,myfun,STMT,(x,(y,())),(z,())) :-
    NEQ  = operation(neq,(variable(x),(variable(y),()))),
    SUM  = operation(add,(variable(x),(variable(y),()))),
    STMT = seq2(assert(NEQ),assign(z,SUM)).
    %STMT = seq2(assign(w,NEQ),assign(z,SUM)).
execution_run(dummy,myfun).

assign(dummy,execution_input(myfun,x),variable(gx)).
assign(dummy,execution_input(myfun,y),variable(gy)).
assign(dummy,gz,variable(execution_output(myfun,z))).

assign(dummy,same,operation(eq,(variable(gx),(variable(gy),())))).

evaluate(neq,(variable(gx),(variable(gy),()))).
%#show _execution_evaled/4.
%#show _execution_result/3.
%#show _execution_ou/3.
#show value/3.
%#show _execution_result/3.
#show _gex_exec/2.
%#show _execution_equery/3.
%#show _execution_eval_aux/4.
%#show eValue/3.
%#show direct_query/1.
#show evaluated/4.


