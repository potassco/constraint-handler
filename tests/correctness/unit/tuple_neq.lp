variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

variable_define(tuple_plain,(val(int,1),val(string,"x"),val(symbol,key))).
variable_define(tuple_plain_same,variable(tuple_plain)).
variable_define(tuple_diff,(val(int,2),val(string,"x"),val(symbol,key))).

variable_define(tuple_with_none,(val(none,none),val(int,1))).
variable_define(tuple_with_none_same,variable(tuple_with_none)).

evaluate(neq,(variable(tuple_plain),(variable(tuple_plain_same),()))).
evaluate(neq,(variable(tuple_plain),(variable(tuple_diff),()))).
evaluate(neq,(variable(tuple_with_none),(variable(tuple_with_none_same),()))).
evaluate(neq,(variable(tuple_plain),(variable(tuple_with_none),()))).
evaluate(neq,(variable(tuple_plain),(variable(none_case),()))).
evaluate(neq,(variable(none_case),(variable(tuple_plain),()))).
evaluate(neq,(variable(tuple_plain),(variable(bad_case),()))).
evaluate(neq,(variable(bad_case),(variable(tuple_plain),()))).

phase_request(type_check,false).

#show evaluated/3.
