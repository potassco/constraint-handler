variable_declare(two_case,fromFacts).
variable_domain(two_case,val(int,2)).

variable_declare(three_case,fromFacts).
variable_domain(three_case,val(int,3)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(mult,(variable(two_case),(variable(three_case),()))).
evaluate(mult,(variable(two_case),(variable(none_case),()))).
evaluate(mult,(variable(two_case),(variable(bad_case),()))).

#show evaluated/3.
