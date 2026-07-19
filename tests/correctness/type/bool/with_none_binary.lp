phase_request(type_check,true).

variable_define(c_conj_none_bool,operation(conj,(val(none,none),(val(bool,true),())))).
variable_define(c_conj_bool_none,operation(conj,(val(bool,true),(val(none,none),())))).
variable_define(c_conj_none_none,operation(conj,(val(none,none),(val(none,none),())))).
variable_define(c_disj_none_bool,operation(disj,(val(none,none),(val(bool,true),())))).
variable_define(c_disj_bool_none,operation(disj,(val(bool,false),(val(none,none),())))).
variable_define(c_disj_none_none,operation(disj,(val(none,none),(val(none,none),())))).
variable_define(c_lxor_none_bool,operation(lxor,(val(none,none),(val(bool,true),())))).
variable_define(c_lxor_bool_none,operation(lxor,(val(bool,false),(val(none,none),())))).
variable_define(c_lxor_none_none,operation(lxor,(val(none,none),(val(none,none),())))).
variable_define(c_leqv_none_bool,operation(leqv,(val(none,none),(val(bool,true),())))).
variable_define(c_leqv_bool_none,operation(leqv,(val(bool,true),(val(none,none),())))).
variable_define(c_leqv_none_none,operation(leqv,(val(none,none),(val(none,none),())))).
variable_define(c_limp_none_bool,operation(limp,(val(none,none),(val(bool,false),())))).
variable_define(c_limp_bool_none,operation(limp,(val(bool,true),(val(none,none),())))).
variable_define(c_limp_none_none,operation(limp,(val(none,none),(val(none,none),())))).
