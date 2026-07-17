variable_declare(two_case,fromFacts).
variable_domain(two_case,val(int,2)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(minus,(variable(two_case),())).
evaluate(minus,(variable(none_case),())).
evaluate(minus,(variable(bad_case),())).

#show evaluated/3.
