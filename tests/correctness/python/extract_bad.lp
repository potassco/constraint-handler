variable_define(div_bad,operation(pythonExtract("tmp = 1 / x","tmp"),((val(string,"x"),val(int,0)),()))).
variable_define(expr_bad,operation(pythonExtract("tmp = 4","tmp + missing_name"),())).

#show value/2.
