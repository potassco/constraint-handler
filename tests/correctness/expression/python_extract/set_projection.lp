% Regression for compile2 emitting duplicate stable models when a Python-extract
% binding tuple contains a set child whose actual membership is fixed.

variable_declare(pool,set).
set_baseDomain(pool,val(int,1)).
set_baseDomain(pool,val(int,2)).

ensure(operation(set_isin,(val(int,1),(variable(pool),())))).
ensure(operation(set_notin,(val(int,2),(variable(pool),())))).

variable_define(out,operation(pythonExtract("tmp = 0","tmp"),((val(string,"pool"),variable(pool)),()))).

#show value/2.
