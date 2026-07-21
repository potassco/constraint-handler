phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(symbol,b)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(lt,(variable(x),(val(symbol,a),()))).
evaluate(lt,(variable(x),(val(none,none),()))).
evaluate(lt,(variable(x),(bad,()))).


evaluate(lt,(val(symbol,a),(val(symbol,a),()))).
evaluate(lt,(val(symbol,a),(val(symbol,b),()))).
evaluate(lt,(val(symbol,b),(val(symbol,a),()))).
evaluate(lt,(val(none,none),(val(symbol,a),()))).
evaluate(lt,(val(symbol,a),(val(none,none),()))).
evaluate(lt,(val(symbol,a),(bad,()))).
