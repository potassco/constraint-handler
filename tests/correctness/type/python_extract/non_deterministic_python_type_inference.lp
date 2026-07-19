phase_request(type_check,true).

variable_declare(raw,fromFacts).
variable_domain(raw,val(int,7)).
variable_domain(raw,val(bool,true)).

variable_define(extract_out,operation(pythonExtract("tmp = raw","tmp"),((val(string,"raw"),variable(raw)),()))).
