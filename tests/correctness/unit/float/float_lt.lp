evaluate(operation(lt,(val(float,float("1.5")),(val(int,2),())))).
evaluate(operation(lt,(val(float,float("2.5")),(val(int,2),())))).
evaluate(operation(lt,(val(float,float("1.5")),(val(none,none),())))).
evaluate(operation(lt,(val(float,float("1.5")),(bad,())))).


variable_declare(x,fromFacts).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(lt,(variable(x),(val(float,float("1.5")),())))).
evaluate(operation(lt,(variable(x),(val(none,none),())))).
evaluate(operation(lt,(variable(x),(bad,())))).
