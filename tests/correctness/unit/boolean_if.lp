variable_declare(false_case,fromFacts).
variable_domain(false_case,val(bool,false)).

variable_declare(true_case,fromFacts).
variable_domain(true_case,val(bool,true)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

variable_declare(payload_int,fromFacts).
variable_domain(payload_int,val(int,1)).

variable_declare(payload_bad,fromFacts).
variable_domain(payload_bad,bad).

evaluate(if,(variable(true_case),(variable(payload_int),()))).
evaluate(if,(variable(true_case),(variable(payload_bad),()))).
evaluate(if,(variable(false_case),(variable(payload_int),()))).
evaluate(if,(variable(false_case),(variable(payload_bad),()))).
evaluate(if,(variable(none_case),(variable(payload_int),()))).
evaluate(if,(variable(bad_case),(variable(payload_int),()))).

#show evaluated/3.
