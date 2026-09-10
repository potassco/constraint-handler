% Regression for compile2 treating an absent optional value as optimal when
% optimization depends on a linked presence flag.

ensure(operation(eq,(operation(hasValue,(variable(opt),())),(variable(present),()))),e1).
ensure(operation(limp,(variable(present),(operation(eq,(variable(opt),(variable(input),()))),()))),e2).

optimize_maximizeSum(operation(add,(operation(mult,(variable(opt),(val(int,6),()))),(val(int,0),()))),tag,1).
optimize_precision(val(int,1),1).

variable_declare(opt,fromFacts).
variable_domain(opt,val(none,none)).
variable_declare(present,boolDomain).
variable_define(input,val(int,2)).
variable_domain(opt,val(int,2)).
