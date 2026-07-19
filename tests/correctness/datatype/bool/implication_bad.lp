%%% bad-aware boolean implication checks

variable_declare(x,fromFacts).
variable_domain(x,val(bool,(true;false))).

variable_define(y,operation(ite,(operation(eq,(variable(x),(val(bool,false),()))),
  (val(int,5),(bad,()))))).

evaluate(limp,
  (operation(eq,(variable(x),(val(bool,false),()))),
  (operation(eq,(variable(y),(val(int,5),()))),()))).
