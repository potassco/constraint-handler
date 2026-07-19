phase_request(type_check,true).

variable_define(v_none_bool(1;2),fromFacts).
variable_domain(v_none_bool(1;2),val(none,none)).
variable_domain(v_none_bool(1;2),val(bool,true)).

variable_define(v_optional_int(1;2),fromFacts).
variable_domain(v_optional_int(1;2),val(none,none)).
variable_domain(v_optional_int(1;2),val(int,5)).

variable_define(c_none_has_value,operation(hasValue,(val(none,none),()))).
variable_define(c_bool_has_value,operation(hasValue,(val(bool,true),()))).
variable_define(c_none_bool_1_has_value,operation(hasValue,(variable(v_none_bool(1)),()))).
variable_define(c_none_bool_2_has_value,operation(hasValue,(variable(v_none_bool(2)),()))).
variable_define(c_optional_int_1_has_value,operation(hasValue,(variable(v_optional_int(1)),()))).
variable_define(c_optional_int_2_has_value,operation(hasValue,(variable(v_optional_int(2)),()))).
