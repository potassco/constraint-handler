% Compile can realize the absent branch for p and chk.result, while compile2
% currently only realizes the present branch.

variable_domain(execution_input(((((),"r"),"u"),"chk"),"result"),val(none,none)).

execution_run(rupos).
execution_run(((((),"r"),"u"),"chk")).

variable_declare(s0(rup),set).
set_baseDomain(s0(rup),val(string,"Back")).

variable_domain(execution_input(rupos,"p"),variable(rup)).
variable_domain(execution_input(((((),"r"),"u"),"chk"),"result"),variable(execution_output(rupos,"result"))).

variable_declare((((),"r"),"s"),boolDomain).

variable_define(execution_input(rupos,run),variable((((),"r"),"s"))).
variable_define(execution_input(((((),"r"),"u"),"chk"),run),variable((((),"r"),"s"))).
variable_define(rup,operation(if,(variable((((),"r"),"s")),(variable(s0(rup)),())))).

execution_declare(rupos,if(variable(run),assign("result",operation(eq,(variable("p"),(operation(set_make,(val(string,"Back"),())),())))),noop),(run,("p",())),("result",())).
execution_declare(((((),"r"),"u"),"chk"),if(variable(run),if(operation(lnot,(operation(lnot,(variable("result"),())),())),assert(val(bool,false)),noop),noop),(run,("result",())),()).

evaluate(operation(lnot,(operation(lnot,(variable(execution_input(((((),"r"),"u"),"chk"),"result")),())),()))).
evaluate(operation(hasValue,(variable(rup),()))).

#show evaluated/3.
