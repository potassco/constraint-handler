variable_declare(gate,fromFacts).
variable_domain(gate,val(int,0..1)).

variable_declare(raw,fromFacts).
variable_domain(raw,val(int,7..8)).

variable_define(out,operation(pythonExtract("tmp = 0 if gate == 0 else raw","tmp"),((val(string,"gate"),variable(gate)),((val(string,"raw"),variable(raw)),())))).

#show value/2.
