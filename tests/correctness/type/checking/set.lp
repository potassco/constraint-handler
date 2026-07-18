phase_request(type_check,true).

variable_declare(v_int,fromFacts).
variable_domain(v_int,val(int,3)).

variable_declare(v_set,set).
set_assign(v_set,variable(v_int)).

variable_define(c_eq,operation(eq,(variable(v_set),(variable(v_set),())))).
variable_define(c_neq,operation(neq,(variable(v_set),(variable(v_set),())))).
variable_define(c_union,operation(union,(variable(v_set),(variable(v_set),())))).
variable_define(c_inter,operation(inter,(variable(v_set),(variable(v_set),())))).
variable_define(c_diff,operation(diff,(variable(v_set),(variable(v_set),())))).
variable_define(c_subset,operation(subset,(variable(v_set),(variable(v_set),())))).
variable_define(c_length,operation(length,(variable(v_set),()))).
variable_define(c_isin,operation(set_isin,(variable(v_int),(variable(v_set),())))).
variable_define(c_notin,operation(set_notin,(variable(v_int),(variable(v_set),())))).
variable_define(c_make,operation(set_make,(variable(v_int),(variable(v_int),(variable(v_int),()))))).
variable_define(c_has_value,operation(hasValue,(variable(v_set),()))).
