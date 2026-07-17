variable_declare(false_case,fromFacts).
variable_domain(false_case,val(bool,false)).

variable_declare(true_case,fromFacts).
variable_domain(true_case,val(bool,true)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(lnot,(variable(false_case),())).
evaluate(lnot,(variable(true_case),())).
evaluate(lnot,(variable(none_case),())).
evaluate(lnot,(variable(bad_case),())).

#show evaluated/3.
