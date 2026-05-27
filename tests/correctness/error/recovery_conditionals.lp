% Contains a division by zero error resulting in a bad value
% The bad value should be propagated onwards
variable_define(six,val(int,6)).
variable_define(two,val(int,2)).
variable_define(add_three_twos,operation(add,(variable(two),(variable(two),(variable(two),()))))).
variable_define(six_minus_six,operation(sub,(variable(six),(variable(add_three_twos),())))).
variable_define(div_bad,operation(int_div,(variable(six),(variable(six_minus_six),())))).
variable_define(mult_bad,operation(mult,(variable(div_bad),(variable(two),())))).
variable_define(lt_bad,operation(lt,(variable(mult_bad),(variable(two),())))).

% Operator `if` is recoverable when condition is false, because the branch with the bad value won't be taken.
variable_define(if_bad,operation(if,(variable(lt_bad),(val(int,1),())))).
variable_define(if_bad_also,operation(if,(val(bool,true),(variable(lt_bad),())))).
variable_define(if_recovered,operation(if,(val(bool,false),(variable(lt_bad),())))).

% Operator `default` is recoverable if the default value is bad but not taken.
variable_define(default_bad,operation(default,(variable(lt_bad),(val(int,1),())))).
variable_define(default_bad_also,operation(default,(val(none,none),(variable(lt_bad),())))).
variable_define(default_recovered,operation(default,(val(int,1),(variable(lt_bad),())))).
