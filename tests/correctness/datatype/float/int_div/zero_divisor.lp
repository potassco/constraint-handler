variable_declare(x,fromFacts).
variable_domain(x,val(float,float("0.0"))).
variable_domain(x,val(float,float("2.0"))).

evaluate(operation(int_div,(val(float,float("6.0")),(variable(x),())))).
