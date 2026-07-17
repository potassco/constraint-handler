variable_declare(f_large,fromFacts).
variable_domain(f_large,val(float,float("2.5"))).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(floor,(variable(f_large),())).
evaluate(floor,(variable(none_case),())).
evaluate(floor,(variable(bad_case),())).

#show evaluated/3.
