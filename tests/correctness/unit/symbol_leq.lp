phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(symbol,b)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(leq,(variable(x),(val(symbol,a),()))).
evaluate(leq,(variable(x),(val(none,none),()))).
evaluate(leq,(variable(x),(bad,()))).


evaluate(leq,(val(symbol,a),(val(symbol,a),()))).
evaluate(leq,(val(symbol,a),(val(symbol,b),()))).
evaluate(leq,(val(symbol,b),(val(symbol,a),()))).
evaluate(leq,(val(none,none),(val(symbol,a),()))).
evaluate(leq,(val(symbol,a),(val(none,none),()))).
evaluate(leq,(val(symbol,a),(bad,()))).
