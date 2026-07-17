% compile2 currently goes UNSAT here, while the other engines derive bad.

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(disj,(variable(none_case),(variable(bad_case),()))).

#show evaluated/3.
