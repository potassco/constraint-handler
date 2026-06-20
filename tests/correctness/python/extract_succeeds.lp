variable_declare(flag,fromFacts).
variable_domain(flag,val(int,0..1)).

variable_define(ok,operation(pythonExtract("if flag == 0:\n  raise solver_environment.FailIntegrityExn","__succeeds"),((val(string,"flag"),variable(flag)),()))).

#show value/2.
