variable_declare(x,fromFacts).
variable_domain(x,val(symbol,b)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(gt,(variable(x),(val(symbol,a),())))).
evaluate(operation(gt,(variable(x),(val(none,none),())))).
evaluate(operation(gt,(variable(x),(bad,())))).


evaluate(operation(gt,(val(symbol,a),(val(symbol,a),())))).
evaluate(operation(gt,(val(symbol,a),(val(symbol,b),())))).
evaluate(operation(gt,(val(symbol,b),(val(symbol,a),())))).
evaluate(operation(gt,(val(none,none),(val(symbol,a),())))).
evaluate(operation(gt,(val(symbol,a),(val(none,none),())))).
evaluate(operation(gt,(val(symbol,a),(bad,())))).
