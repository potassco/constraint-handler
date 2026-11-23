phase_request(constantFolding,false).

variable_define(left,(operation(add,(val(int,3),(val(int,4),()))),val(int,8))).
variable_define(right,(operation(add,(val(int,5),(val(int,2),()))),val(int,8))).
variable_define(equal,operation(eq,(variable(left),(variable(right),())))).