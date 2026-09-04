variable_declare(x,fromFacts).
variable_domain(x,val(symbol,b)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(leq,(variable(x),(val(symbol,a),())))).
evaluate(operation(leq,(variable(x),(val(none,none),())))).
evaluate(operation(leq,(variable(x),(bad,())))).


evaluate(operation(leq,(val(symbol,a),(val(symbol,a),())))).
evaluate(operation(leq,(val(symbol,a),(val(symbol,b),())))).
evaluate(operation(leq,(val(symbol,b),(val(symbol,a),())))).
evaluate(operation(leq,(val(none,none),(val(symbol,a),())))).
evaluate(operation(leq,(val(symbol,a),(val(none,none),())))).
evaluate(operation(leq,(val(symbol,a),(bad,())))).
