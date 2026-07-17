variable_declare(false_case,fromFacts).
variable_domain(false_case,val(bool,false)).

variable_declare(true_case,fromFacts).
variable_domain(true_case,val(bool,true)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(conj,()).
evaluate(conj,(variable(true_case),(variable(true_case),()))).
evaluate(conj,(variable(true_case),(variable(none_case),()))).
evaluate(conj,(variable(false_case),(variable(true_case),()))).
evaluate(conj,(variable(false_case),(variable(none_case),()))).
evaluate(conj,(variable(none_case),(variable(bad_case),()))).
evaluate(conj,(variable(true_case),(variable(bad_case),()))).
evaluate(conj,(variable(false_case),(variable(bad_case),()))).

#show evaluated/3.
