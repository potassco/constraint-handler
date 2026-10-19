% A check permits bad values so that expression errors can be recovered.
variable_define(six,val(int,6)).
variable_declare(ints,fromFacts).
variable_domain(ints,val(int,0..3)).
variable_define(div_maybe_bad,operation(int_div,(variable(six),(variable(ints),())))).

check(operation(geq,(variable(div_maybe_bad),(val(int,3),())))).