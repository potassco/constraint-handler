variable_declare(run,boolDomain).
execution_declare(default,assign(x,val(int,1)),(),(x,())).
execution_declare(always,assign(x,val(int,2)),(),(x,()),val(bool,true)).
execution_declare(never,seq2(assign(x,val(int,3)),assert(val(bool,false))),(),(x,()),val(bool,false)).
execution_declare(dynamic,assign(x,val(int,4)),(),(x,()),variable(run),dynamic_label).
execution_declare(inverted,assign(x,val(int,5)),(),(x,()),operation(lnot,(variable(run),()))).
execution_declare(missing,noop,(),(x,()),variable(run)).

variable_define(execution_input(assertion,ok),variable(run)).
execution_declare(assertion,assert(variable(ok)),(ok,()),(),variable(execution_input(assertion,ok))).
evaluate(operation(leqv,(variable(run),(operation(hasValue,(variable(execution_output(dynamic,x)),())),())))).
evaluate(operation(leqv,(operation(lnot,(variable(run),())),(operation(hasValue,(variable(execution_output(inverted,x)),())),())))).

#show value/2.
#show evaluated/2.
