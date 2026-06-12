% Tuple expressions should be accepted as first-class expressions.

variable_define(pair,(val(int,1),val(string,"x"),val(int,12))).
variable_define(computed,(operation(add,(val(int,1),(val(int,2),()))),operation(concat,(val(string,"a"),(val(string,"b"),()))))).
variable_define(copy,variable(pair)).

evaluate(eq,(variable(pair),(variable(copy),()))).
evaluate(neq,(variable(pair),(variable(computed),()))).
