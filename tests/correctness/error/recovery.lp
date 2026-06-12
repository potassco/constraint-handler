% Contains a division by zero error resulting in a bad value
% The bad value should be propagated onwards
variable_define(six,val(int,6)).
variable_define(two,val(int,2)).
variable_define(add_three_twos,operation(add,(variable(two),(variable(two),(variable(two),()))))).
variable_define(six_minus_six,operation(sub,(variable(six),(variable(add_three_twos),())))).
variable_define(div_bad,operation(int_div,(variable(six),(variable(six_minus_six),())))).
variable_define(mult_bad,operation(mult,(variable(div_bad),(variable(two),())))).

% Make sure bad also works with evaluate
evaluate(lt,(variable(mult_bad),(variable(two),()))).

% Operator `pow` is recoverable when exponent is 0.
variable_define(pow_bad,operation(pow,(variable(div_bad),(val(int,3),())))).
variable_define(pow_recovered,operation(pow,(variable(div_bad),(val(int,0),())))).
