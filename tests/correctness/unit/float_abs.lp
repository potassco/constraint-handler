variable_declare(f_neg,fromFacts).
variable_domain(f_neg,val(float,float("-1.5"))).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(abs,(variable(f_neg),())).
evaluate(abs,(variable(none_case),())).
evaluate(abs,(variable(bad_case),())).

#show evaluated/3.
