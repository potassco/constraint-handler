variable_define(x,val(int,3)).
evaluate((variable(x),variable(x))).
evaluate((val(int,5),val(int,3))).

variable_define(r,operation(pythonExtract("res=(x,2*x)","res"),((val(string,"x"),val(int,6)),()))).
