%%% binary conjunction/disjunction with bad involved

variable_define(div_bad,operation(int_div,(val(int,7),(operation(sub,(val(int,6),(val(int,6),()))),())))).
variable_define(lt_bad,operation(lt,(variable(div_bad),(val(int,2),())))).

variable_define(conj_bt,operation(conj,(variable(lt_bad),(val(bool,true),())))).
variable_define(conj_tb,operation(conj,(val(bool,true),(variable(lt_bad),())))).
variable_define(conj_fb,operation(conj,(val(bool,false),(variable(lt_bad),())))).
variable_define(conj_bf,operation(conj,(variable(lt_bad),(val(bool,false),())))).

variable_define(disj_bf,operation(disj,(variable(lt_bad),(val(bool,false),())))).
variable_define(disj_fb,operation(disj,(val(bool,false),(variable(lt_bad),())))).
variable_define(disj_tb,operation(disj,(val(bool,true),(variable(lt_bad),())))).
variable_define(disj_bt,operation(disj,(variable(lt_bad),(val(bool,true),())))).
