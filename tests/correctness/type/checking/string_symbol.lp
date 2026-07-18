phase_request(type_check,true).

variable_declare(v_string,fromFacts).
variable_domain(v_string,val(string,"some_string")).
variable_declare(v_symbol,fromFacts).
variable_domain(v_symbol,val(symbol,some_symbol)).

variable_define(c_string_concat,operation(concat,(variable(v_string),(variable(v_string),())))).
variable_define(c_string_length,operation(length,(variable(v_string),()))).
variable_define(c_string_eq,operation(eq,(variable(v_string),(variable(v_string),())))).
variable_define(c_string_neq,operation(neq,(variable(v_string),(variable(v_string),())))).
variable_define(c_string_has_value,operation(hasValue,(variable(v_string),()))).

variable_define(c_symbol_eq,operation(eq,(variable(v_symbol),(variable(v_symbol),())))).
variable_define(c_symbol_neq,operation(neq,(variable(v_symbol),(variable(v_symbol),())))).
variable_define(c_symbol_has_value,operation(hasValue,(variable(v_symbol),()))).
