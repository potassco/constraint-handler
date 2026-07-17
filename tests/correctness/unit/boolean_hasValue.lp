variable_declare(false_case,fromFacts).
variable_domain(false_case,val(bool,false)).

variable_declare(true_case,fromFacts).
variable_domain(true_case,val(bool,true)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(hasValue,(variable(false_case),())).
evaluate(hasValue,(variable(true_case),())).
evaluate(hasValue,(variable(none_case),())).
evaluate(hasValue,(variable(bad_case),())).

#show evaluated/3.
