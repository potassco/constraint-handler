variable_declare(two_case,fromFacts).
variable_domain(two_case,val(int,2)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(floor,(variable(two_case),())).
evaluate(floor,(variable(none_case),())).
evaluate(floor,(variable(bad_case),())).

#show evaluated/3.
