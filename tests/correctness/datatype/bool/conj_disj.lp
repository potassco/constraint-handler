%%% binary conjunction/disjunction without bad or none

variable_define(conj_tt,operation(conj,(val(bool,true),(val(bool,true),())))).
variable_define(conj_tf,operation(conj,(val(bool,true),(val(bool,false),())))).
variable_define(conj_ft,operation(conj,(val(bool,false),(val(bool,true),())))).
variable_define(conj_ff,operation(conj,(val(bool,false),(val(bool,false),())))).

variable_define(disj_tt,operation(disj,(val(bool,true),(val(bool,true),())))).
variable_define(disj_tf,operation(disj,(val(bool,true),(val(bool,false),())))).
variable_define(disj_ft,operation(disj,(val(bool,false),(val(bool,true),())))).
variable_define(disj_ff,operation(disj,(val(bool,false),(val(bool,false),())))).
