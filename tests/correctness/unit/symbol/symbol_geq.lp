variable_declare(x,fromFacts).
variable_domain(x,val(symbol,b)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(geq,(variable(x),(val(symbol,a),())))).
evaluate(operation(geq,(variable(x),(val(none,none),())))).
evaluate(operation(geq,(variable(x),(bad,())))).


evaluate(operation(geq,(val(symbol,a),(val(symbol,a),())))).
evaluate(operation(geq,(val(symbol,a),(val(symbol,b),())))).
evaluate(operation(geq,(val(symbol,b),(val(symbol,a),())))).
evaluate(operation(geq,(val(none,none),(val(symbol,a),())))).
evaluate(operation(geq,(val(symbol,a),(val(none,none),())))).
evaluate(operation(geq,(val(symbol,a),(bad,())))).
