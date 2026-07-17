variable_declare(neg_two_case,fromFacts).
variable_domain(neg_two_case,val(int,-2)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(abs,(variable(neg_two_case),())).
evaluate(abs,(variable(none_case),())).
evaluate(abs,(variable(bad_case),())).

#show evaluated/3.
