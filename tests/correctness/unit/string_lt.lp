phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(string,"ab")).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(lt,(variable(x),(val(string,"aa"),()))).
evaluate(lt,(variable(x),(val(none,none),()))).
evaluate(lt,(variable(x),(bad,()))).


evaluate(lt,(val(string,"aa"),(val(string,"ab"),()))).
evaluate(lt,(val(string,"ab"),(val(string,"aa"),()))).
evaluate(lt,(val(string,"aa"),(val(string,"aa"),()))).
evaluate(lt,(val(none,none),(val(string,"ab"),()))).
evaluate(lt,(val(string,"aa"),(val(none,none),()))).
evaluate(lt,(val(string,"aa"),(bad,()))).
