% Regression: optional membership should use set_isin/set_notin over {"X", "Y"}.

variable_declare(x,fromFacts).
variable_domain(x,val(str,"X")).
variable_declareOptional(x).

variable_define(pool,operation(set_make,(val(str,"X"),(val(str,"Y"),())))).
variable_define(set_in,operation(set_isin,(variable(x),(variable(pool),())))).
variable_define(set_not,operation(set_notin,(variable(x),(variable(pool),())))).

evaluate(set_isin,(variable(x),(variable(pool),()))).
evaluate(set_notin,(variable(x),(variable(pool),()))).
evaluate(eq,(variable(set_in),(operation(lnot,(variable(set_not),())),()))).
evaluate(eq,(variable(set_not),(operation(lnot,(variable(set_in),())),()))).
