% Regression: failed pythonExtract input binding must not leak through EXPR evaluation.
variable_define(anchor,val(int,1)).
variable_define(leaky,operation(pythonExtract("pass","lhs is not None"),(val(string,"lhs"),(variable(missing_input),())))).
