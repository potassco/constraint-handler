% Contains a division by zero error resulting in a bad value
% The bad value should be propagated onwards
variable_define(six, val(int, 6)).
variable_declare(ints, fromFacts).
variable_domain(ints, val(int, 0..3)).
variable_define(div_maybe_bad, operation(int_div, (variable(six),(variable(ints),())))).

ensure(operation(geq,(variable(div_maybe_bad), (val(int,3),())))).
% ensure(operation(conj,(variable(x),(operation(lnot,(variable(y),())),())))).
