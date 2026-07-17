variable_declare(bool_true,fromFacts).
variable_domain(bool_true,val(bool,true)).

variable_declare(bool_false,fromFacts).
variable_domain(bool_false,val(bool,false)).

variable_declare(int_one,fromFacts).
variable_domain(int_one,val(int,1)).

variable_declare(int_two,fromFacts).
variable_domain(int_two,val(int,2)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(string_foo,fromFacts).
variable_domain(string_foo,val(string,"foo")).

variable_declare(string_bar,fromFacts).
variable_domain(string_bar,val(string,"bar")).

variable_declare(symbol_red,fromFacts).
variable_domain(symbol_red,val(symbol,red)).

variable_declare(symbol_blue,fromFacts).
variable_domain(symbol_blue,val(symbol,blue)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

variable_define(tuple_left,(val(int,1),val(string,"x"),val(symbol,key))).
variable_define(tuple_same,variable(tuple_left)).
variable_define(tuple_other,(val(int,2),val(string,"x"),val(symbol,key))).

evaluate(neq,(variable(bool_true),(variable(bool_true),()))).
evaluate(neq,(variable(bool_true),(variable(bool_false),()))).
evaluate(neq,(variable(int_one),(variable(int_one),()))).
evaluate(neq,(variable(int_one),(variable(int_two),()))).
evaluate(neq,(variable(none_case),(variable(none_case),()))).
evaluate(neq,(variable(string_foo),(variable(string_foo),()))).
evaluate(neq,(variable(string_foo),(variable(string_bar),()))).
evaluate(neq,(variable(symbol_red),(variable(symbol_red),()))).
evaluate(neq,(variable(symbol_red),(variable(symbol_blue),()))).
evaluate(neq,(variable(tuple_left),(variable(tuple_same),()))).
evaluate(neq,(variable(tuple_left),(variable(tuple_other),()))).
evaluate(neq,(variable(bool_true),(variable(none_case),()))).
evaluate(neq,(variable(none_case),(variable(bool_true),()))).
evaluate(neq,(variable(bool_true),(variable(bad_case),()))).
evaluate(neq,(variable(bad_case),(variable(bool_true),()))).

phase_request(type_check,false).

#show evaluated/3.
