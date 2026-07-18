phase_request(type_check,true).

variable_declare(v_int,fromFacts).
variable_domain(v_int,val(int,3)).
variable_declare(v_float,fromFacts).
variable_domain(v_float,val(float,float("3.14"))).
variable_declare(v_string,fromFacts).
variable_domain(v_string,val(string,"s")).
variable_declare(v_symbol,fromFacts).
variable_domain(v_symbol,val(symbol,some_symbol)).

variable_declare(v_map,multimap).
multimap_assign(v_map,variable(v_string),variable(v_int)).
multimap_assign(v_map,variable(v_symbol),variable(v_int)).

variable_define(c_eq,operation(eq,(variable(v_map),(variable(v_map),())))).
variable_define(c_neq,operation(neq,(variable(v_map),(variable(v_map),())))).
variable_define(c_isin,operation(multimap_isin,(variable(v_string),(variable(v_map),())))).
variable_define(c_find,operation(find,(variable(v_string),(variable(v_map),())))).
variable_define(c_count_keys,operation(countKeys,(variable(v_map),()))).
variable_define(c_count_entries,operation(countEntries,(variable(v_map),()))).
variable_define(c_sum_int_entries,operation(sumIntEntries,(variable(v_map),()))).
variable_define(c_max_entries,operation(maxEntries,(variable(v_map),()))).
variable_define(c_min_entries,operation(minEntries,(variable(v_map),()))).
variable_define(c_make,operation(multimap_make,((variable(v_string),variable(v_int)),((variable(v_string),variable(v_float)),((variable(v_symbol),variable(v_int)),()))))).
variable_define(c_has_value,operation(hasValue,(variable(v_map),()))).
