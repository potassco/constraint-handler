% Tuple expressions should be accepted as first-class expressions.

variable_define(pair,(val(int,1),val(string,"x"))).
variable_define(computed,(operation(add,(val(int,1),(val(int,2),()))),operation(concat,(val(string,"a"),(val(string,"b"),()))))).
variable_define(copy,variable(pair)).
variable_define(nested,(variable(pair),variable(computed))).
variable_define(nested_copy,((val(int,1),val(string,"x")),(val(int,3),val(string,"ab")))).

evaluate(eq,(variable(pair),(variable(copy),()))).
evaluate(neq,(variable(pair),(variable(computed),()))).
evaluate(eq,(variable(nested),(variable(nested_copy),()))).