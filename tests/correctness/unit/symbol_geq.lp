phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(symbol,b)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(geq,(variable(x),(val(symbol,a),()))).
evaluate(geq,(variable(x),(val(none,none),()))).
evaluate(geq,(variable(x),(bad,()))).


evaluate(geq,(val(symbol,a),(val(symbol,a),()))).
evaluate(geq,(val(symbol,a),(val(symbol,b),()))).
evaluate(geq,(val(symbol,b),(val(symbol,a),()))).
evaluate(geq,(val(none,none),(val(symbol,a),()))).
evaluate(geq,(val(symbol,a),(val(none,none),()))).
evaluate(geq,(val(symbol,a),(bad,()))).
