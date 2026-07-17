variable_declare(primary_int,fromFacts).
variable_domain(primary_int,val(int,1)).

variable_declare(primary_none,fromFacts).
variable_domain(primary_none,val(none,none)).

variable_declare(primary_bad,fromFacts).
variable_domain(primary_bad,bad).

variable_declare(fallback_int,fromFacts).
variable_domain(fallback_int,val(int,2)).

variable_declare(fallback_none,fromFacts).
variable_domain(fallback_none,val(none,none)).

variable_declare(fallback_bad,fromFacts).
variable_domain(fallback_bad,bad).

evaluate(default,(variable(primary_int),(variable(fallback_int),()))).
evaluate(default,(variable(primary_bad),(variable(fallback_int),()))).
evaluate(default,(variable(primary_none),(variable(fallback_int),()))).
evaluate(default,(variable(primary_none),(variable(fallback_bad),()))).
evaluate(default,(variable(primary_none),(variable(fallback_none),()))).

#show evaluated/3.
