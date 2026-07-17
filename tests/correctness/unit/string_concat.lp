variable_declare(left_case,fromFacts).
variable_domain(left_case,val(string,"ab")).

variable_declare(right_case,fromFacts).
variable_domain(right_case,val(string,"c")).

variable_declare(empty_case,fromFacts).
variable_domain(empty_case,val(string,"")).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(concat,(variable(left_case),(variable(right_case),()))).
evaluate(concat,(variable(empty_case),(variable(right_case),()))).
evaluate(concat,(variable(left_case),(variable(empty_case),()))).
evaluate(concat,(variable(none_case),(variable(right_case),()))).
evaluate(concat,(variable(left_case),(variable(none_case),()))).
evaluate(concat,(variable(bad_case),(variable(right_case),()))).

#show evaluated/3.
