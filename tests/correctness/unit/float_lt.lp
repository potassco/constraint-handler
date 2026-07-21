evaluate(lt,(val(float,float("1.5")),(val(int,2),()))).
evaluate(lt,(val(float,float("2.5")),(val(int,2),()))).
evaluate(lt,(val(float,float("1.5")),(val(none,none),()))).
evaluate(lt,(val(float,float("1.5")),(bad,()))).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(lt,(variable(x),(val(float,float("1.5")),()))).
evaluate(lt,(variable(x),(val(none,none),()))).
evaluate(lt,(variable(x),(bad,()))).

