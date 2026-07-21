
variable_declare(x,fromFacts).
variable_domain(x,val(symbol,b)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(gt,(variable(x),(val(symbol,a),()))).
evaluate(gt,(variable(x),(val(none,none),()))).
evaluate(gt,(variable(x),(bad,()))).


evaluate(gt,(val(symbol,a),(val(symbol,a),()))).
evaluate(gt,(val(symbol,a),(val(symbol,b),()))).
evaluate(gt,(val(symbol,b),(val(symbol,a),()))).
evaluate(gt,(val(none,none),(val(symbol,a),()))).
evaluate(gt,(val(symbol,a),(val(none,none),()))).
evaluate(gt,(val(symbol,a),(bad,()))).
