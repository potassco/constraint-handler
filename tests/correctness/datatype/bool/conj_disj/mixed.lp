%%% variadic conjunction/disjunction with bad and none involved

variable_define(div_bad,operation(int_div,(val(int,7),(operation(sub,(val(int,6),(val(int,6),()))),())))).
variable_define(lt_bad,operation(lt,(variable(div_bad),(val(int,2),())))).

evaluate(operation(conj,(val(bool,true),(variable(lt_bad),(val(none,none),()))))).
evaluate(operation(conj,(val(bool,true),(variable(lt_bad),(val(bool,false),(val(none,none),())))))).
evaluate(operation(conj,(val(bool,true),(val(none,none),(val(bool,true),()))))).

evaluate(operation(disj,(val(bool,false),(variable(lt_bad),(val(none,none),()))))).
evaluate(operation(disj,(val(bool,false),(variable(lt_bad),(val(bool,true),(val(none,none),())))))).
evaluate(operation(disj,(val(bool,false),(val(none,none),(val(bool,false),(val(none,none),())))))).
