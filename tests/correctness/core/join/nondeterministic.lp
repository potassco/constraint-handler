variable_declare(source,fromFacts).
variable_domain(source,val(int,(1;4;7))).
variable_declare(joined,join).
variable_element(joined,variable(source)).
variable_element(joined,val(int,5)).
