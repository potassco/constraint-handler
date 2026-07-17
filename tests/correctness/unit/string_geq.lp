variable_declare(less_case,fromFacts).
variable_domain(less_case,val(string,"aa")).

variable_declare(greater_case,fromFacts).
variable_domain(greater_case,val(string,"ab")).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(geq,(variable(greater_case),(variable(less_case),()))).
evaluate(geq,(variable(less_case),(variable(greater_case),()))).
evaluate(geq,(variable(less_case),(variable(less_case),()))).
evaluate(geq,(variable(none_case),(variable(greater_case),()))).
evaluate(geq,(variable(less_case),(variable(none_case),()))).
evaluate(geq,(variable(less_case),(variable(bad_case),()))).

#show evaluated/3.
