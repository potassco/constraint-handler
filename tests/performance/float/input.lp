#const size = 64.

step(1..size).
variable_declare(input,fromFacts).
variable_domain(input,val(float,float("-0.75"))).
variable_domain(input,val(float,float("0.9666666666666667"))).
variable_domain(input,val(float,float("1.25"))).

#show value/2.