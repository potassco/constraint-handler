variable_declare(f_small,fromFacts).
variable_domain(f_small,val(float,float("1.5"))).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(minus,(variable(f_small),())).
evaluate(minus,(variable(none_case),())).
evaluate(minus,(variable(bad_case),())).

#show evaluated/3.
