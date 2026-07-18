%%% bad-aware boolean equivalence checks

variable_declare(x,fromFacts).
variable_domain(x,val(bool,(true;false))).

variable_define(y,operation(ite,(operation(eq,(variable(x),(val(bool,false),()))),
  (val(int,5),(bad,()))))).

evaluate(leqv,
  (operation(eq,(variable(y),(val(int,5),()))),
  (operation(eq,(variable(x),(val(bool,false),()))),()))).

evaluate(leqv,
  (bad,
  (operation(eq,(variable(x),(val(bool,false),()))),()))).
