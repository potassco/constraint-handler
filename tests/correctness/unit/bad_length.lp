variable_declare(text_case,fromFacts).
variable_domain(text_case,val(string,"ab")).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(length,(variable(text_case),())).
evaluate(length,(variable(none_case),())).
evaluate(length,(variable(bad_case),())).

#show evaluated/3.
