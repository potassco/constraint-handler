% compile2 currently goes UNSAT for these left-none implication cases.

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(false_case,fromFacts).
variable_domain(false_case,val(bool,false)).

evaluate(limp,(variable(none_case),(variable(false_case),()))).
evaluate(limp,(variable(none_case),(variable(none_case),()))).

#show evaluated/3.
