phase_request(type_check,true).

variable_define(v_none,val(none,none)).
variable_declare(v_bool,boolDomain).

variable_define(v_none_bool(1;2),fromFacts).
variable_domain(v_none_bool(1;2),val(none,none)).
variable_domain(v_none_bool(1;2),variable(v_bool)).

variable_define(c_none_eq,operation(eq,(variable(v_none),(variable(v_bool),())))).
variable_define(c_none_neq,operation(neq,(variable(v_none),(variable(v_bool),())))).
variable_define(c_none_lnot,operation(lnot,(variable(v_none),()))).

variable_define(c_bool_lnot,operation(lnot,(variable(v_bool),()))).
variable_define(c_bool_snot,operation(snot,(variable(v_bool),()))).
variable_define(c_bool_wnot,operation(wnot,(variable(v_bool),()))).
variable_define(c_bool_eq,operation(eq,(variable(v_bool),(variable(v_bool),())))).
variable_define(c_bool_neq,operation(neq,(variable(v_bool),(variable(v_bool),())))).
variable_define(c_bool_conj,operation(conj,(variable(v_bool),(variable(v_bool),(variable(v_bool),()))))).
variable_define(c_bool_disj,operation(disj,(variable(v_bool),(variable(v_bool),(variable(v_bool),()))))).
variable_define(c_bool_lxor,operation(lxor,(variable(v_bool),(variable(v_bool),(variable(v_bool),()))))).
variable_define(c_bool_leqv,operation(leqv,(variable(v_bool),(variable(v_bool),(variable(v_bool),()))))).
variable_define(c_bool_limp,operation(limp,(variable(v_none_bool(1)),(variable(v_none_bool(2)),())))).
variable_define(c_bool_has_value,operation(hasValue,(variable(v_bool),()))).
