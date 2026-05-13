variable_declare(x,fromFacts).
variable_domain(x,val(bool,(true;false))).
%variable_domain(x,val(none,none)).

variable_define(y,operation(ite,(operation(eq,(variable(x),(val(bool,false),()))),
  (val(int,5),(bad,()))))).

evaluate(leqv,
  (operation(eq,(variable(y),(val(int,5),()))),
  (operation(eq,(variable(x),(val(bool,false),()))),()))).
evaluate(limp,
  (operation(eq,(variable(x),(val(bool,false),()))),
  (operation(eq,(variable(y),(val(int,5),()))),()))).

evaluate(leqv,
  (bad,
  (operation(eq,(variable(x),(val(bool,false),()))),()))).

#show value/2.
#show _se_value/2.
#show evaluated/3.
