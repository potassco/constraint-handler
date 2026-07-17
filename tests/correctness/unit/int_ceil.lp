variable_declare(i_neg,fromFacts).
variable_domain(i_neg,val(int,-3)).

variable_declare(i_two,fromFacts).
variable_domain(i_two,val(int,2)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(ceil,(variable(i_neg),())).
evaluate(ceil,(variable(i_two),())).
evaluate(ceil,(variable(none_case),())).
evaluate(ceil,(variable(bad_case),())).

#show evaluated/3.
