% Compile can realize the absent branch for p and chk.result, while compile2
% currently only realizes the present branch.

variable_declareOptional(execution_input(((((),"r"),"u"),"chk"),"result")).

execution_run(((((),"r"),"u"),"pos"),((((),"r"),"u"),"pos")).
execution_run(((((),"r"),"u"),"chk"),((((),"r"),"u"),"chk")).

set_declare(((((),"r"),"u"),"p"),s0(((((),"r"),"u"),"p"))).
set_baseDomain(((((),"r"),"u"),"p"),s0(((((),"r"),"u"),"p")),val(string,"Back")).

variable_domain(execution_input(((((),"r"),"u"),"pos"),"p"),variable(((((),"r"),"u"),"p"))).
variable_domain(execution_input(((((),"r"),"u"),"chk"),"result"),variable(execution_output(((((),"r"),"u"),"pos"),"result"))).

variable_declare((((),"r"),"s"),(((),"r"),"s"),boolDomain).

variable_define(((((),"r"),"u"),"pos"),execution_input(((((),"r"),"u"),"pos"),run),variable((((),"r"),"s"))).
variable_define(((((),"r"),"u"),"chk"),execution_input(((((),"r"),"u"),"chk"),run),variable((((),"r"),"s"))).
variable_define(((((),"r"),"u"),"p"),(((((),"r"),"u"),"p")),operation(if,(variable((((),"r"),"s")),(variable(s0(((((),"r"),"u"),"p"))),())))).

execution_declare(((((),"r"),"u"),"pos"),((((),"r"),"u"),"pos"),if(variable(run),assign("result",operation(eq,(variable("p"),(operation(set_make,(val(string,"Back"),())),())))),noop),(run,("p",())),("result",())).
execution_declare(((((),"r"),"u"),"chk"),((((),"r"),"u"),"chk"),if(variable(run),if(operation(lnot,(operation(lnot,(variable("result"),())),())),assert(val(bool,false)),noop),noop),(run,("result",())),()).

evaluate(lnot,(operation(lnot,(variable(execution_input(((((),"r"),"u"),"chk"),"result")),())),())).
evaluate(hasValue,(variable(((((),"r"),"u"),"p")),())).

#show evaluated/3.
