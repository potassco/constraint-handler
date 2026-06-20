% Regression for compile2 treating an absent optional value as optimal when
% optimization depends on a linked presence flag.

ensure((e1,(present,opt)),operation(eq,(operation(hasValue,(variable(opt),())),(variable(present),())))).
ensure((e2,(present,(opt,input))),operation(limp,(variable(present),(operation(eq,(variable(opt),(variable(input),()))),())))).

optimize_maximizeSum(operation(add,(operation(mult,(variable(opt),(val(int,6),()))),(val(int,0),()))),tag,1).
optimize_precision(val(int,1),1).

variable_declare(opt,opt,fromFacts).
variable_declareOptional(opt).
variable_declare(present,present,boolDomain).
variable_define(input,input,val(int,2)).
variable_domain(opt,val(int,2)).

#show value/2.
