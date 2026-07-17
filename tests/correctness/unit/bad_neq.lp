variable_declare(one_case,fromFacts).
variable_domain(one_case,val(int,1)).

variable_declare(two_case,fromFacts).
variable_domain(two_case,val(int,2)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(neq,(variable(one_case),(variable(one_case),()))).
evaluate(neq,(variable(one_case),(variable(two_case),()))).
evaluate(neq,(variable(none_case),(variable(one_case),()))).
evaluate(neq,(variable(one_case),(variable(bad_case),()))).

#show evaluated/3.
