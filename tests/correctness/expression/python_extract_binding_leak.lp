% Regression: failed pythonExtract input binding must not leak through EXPR evaluation.
variable_define(anchor,val(int,1)).
variable_define(leaky,pythonExtract((("lhs",variable(missing_input)),()),"pass","lhs is not None")).

#show value/2.
#show warning/3.
