% compile2 currently goes UNSAT for leqv with none-valued operands.

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(false_case,fromFacts).
variable_domain(false_case,val(bool,false)).

evaluate(leqv,(variable(none_case),())).
evaluate(leqv,(variable(false_case),(variable(none_case),()))).

#show evaluated/3.
