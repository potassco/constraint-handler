%%% variadic conjunction/disjunction with arity 0, 1, and many; no bad or none

variable_define(conj0,operation(conj,())).
variable_define(disj0,operation(disj,())).

variable_define(conj1_true,operation(conj,(val(bool,true),()))).
variable_define(conj1_false,operation(conj,(val(bool,false),()))).
variable_define(disj1_true,operation(disj,(val(bool,true),()))).
variable_define(disj1_false,operation(disj,(val(bool,false),()))).

variable_define(conj_many_true,operation(conj,(val(bool,true),(val(bool,true),(val(bool,true),()))))).
variable_define(conj_many_false,operation(conj,(val(bool,true),(val(bool,false),(val(bool,true),()))))).
variable_define(disj_many_true,operation(disj,(val(bool,false),(val(bool,true),(val(bool,false),()))))).
variable_define(disj_many_false,operation(disj,(val(bool,false),(val(bool,false),(val(bool,false),()))))).
