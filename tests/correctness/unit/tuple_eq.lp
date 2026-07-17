variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

variable_define(tuple_plain,(val(int,1),val(string,"x"),val(symbol,key))).
variable_define(tuple_plain_same,variable(tuple_plain)).
variable_define(tuple_diff,(val(int,2),val(string,"x"),val(symbol,key))).

variable_define(tuple_with_none,(val(none,none),val(int,1))).
variable_define(tuple_with_none_same,variable(tuple_with_none)).

evaluate(eq,(variable(tuple_plain),(variable(tuple_plain_same),()))).
evaluate(eq,(variable(tuple_plain),(variable(tuple_diff),()))).
evaluate(eq,(variable(tuple_with_none),(variable(tuple_with_none_same),()))).
evaluate(eq,(variable(tuple_plain),(variable(tuple_with_none),()))).
evaluate(eq,(variable(tuple_plain),(variable(none_case),()))).
evaluate(eq,(variable(none_case),(variable(tuple_plain),()))).
evaluate(eq,(variable(tuple_plain),(variable(bad_case),()))).
evaluate(eq,(variable(bad_case),(variable(tuple_plain),()))).

phase_request(type_check,false).

#show evaluated/3.
