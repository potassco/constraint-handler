variable_declare(false_case,fromFacts).
variable_domain(false_case,val(bool,false)).

variable_declare(true_case,fromFacts).
variable_domain(true_case,val(bool,true)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

variable_declare(then_int,fromFacts).
variable_domain(then_int,val(int,1)).

variable_declare(else_string,fromFacts).
variable_domain(else_string,val(string,"else")).

variable_declare(payload_bad,fromFacts).
variable_domain(payload_bad,bad).

evaluate(ite,(variable(true_case),(variable(then_int),(variable(else_string),())))).
evaluate(ite,(variable(false_case),(variable(then_int),(variable(else_string),())))).
evaluate(ite,(variable(none_case),(variable(then_int),(variable(else_string),())))).
evaluate(ite,(variable(bad_case),(variable(then_int),(variable(else_string),())))).
evaluate(ite,(variable(true_case),(variable(payload_bad),(variable(else_string),())))).
evaluate(ite,(variable(false_case),(variable(then_int),(variable(payload_bad),())))).
evaluate(ite,(variable(true_case),(variable(then_int),(variable(payload_bad),())))).
evaluate(ite,(variable(false_case),(variable(payload_bad),(variable(else_string),())))).

#show evaluated/3.
