phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,true)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(limp,(variable(x),(val(bool,false),()))).
evaluate(limp,(variable(x),(val(none,none),()))).
evaluate(limp,(variable(x),(bad,()))).


evaluate(limp,(val(bool,false),(val(bool,true),()))).
evaluate(limp,(val(bool,false),(bad,()))).
evaluate(limp,(val(bool,true),(val(bool,true),()))).
evaluate(limp,(val(bool,true),(val(bool,false),()))).
evaluate(limp,(val(bool,true),(val(none,none),()))).
evaluate(limp,(val(bool,true),(bad,()))).
evaluate(limp,(val(none,none),(val(bool,true),()))).
evaluate(limp,(bad,(val(bool,true),()))).
evaluate(limp,(bad,(val(bool,false),()))).
