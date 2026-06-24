variable_declare(gate,fromFacts).
variable_domain(gate,val(int,0..1)).

variable_declare(raw,fromFacts).
variable_domain(raw,val(int,4..5)).
variable_domain(raw,bad).

variable_define(out,operation(python("lambda gate, raw: 0 if gate == 0 else raw"),(variable(gate),(variable(raw),())))).

phase_request(type_check,false).
