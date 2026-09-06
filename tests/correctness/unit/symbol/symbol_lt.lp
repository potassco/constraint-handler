variable_declare(x,fromFacts).
variable_domain(x,val(symbol,b)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(lt,(variable(x),(val(symbol,a),())))).
evaluate(operation(lt,(variable(x),(val(none,none),())))).
evaluate(operation(lt,(variable(x),(bad,())))).


evaluate(operation(lt,(val(symbol,a),(val(symbol,a),())))).
evaluate(operation(lt,(val(symbol,a),(val(symbol,b),())))).
evaluate(operation(lt,(val(symbol,b),(val(symbol,a),())))).
evaluate(operation(lt,(val(none,none),(val(symbol,a),())))).
evaluate(operation(lt,(val(symbol,a),(val(none,none),())))).
evaluate(operation(lt,(val(symbol,a),(bad,())))).
