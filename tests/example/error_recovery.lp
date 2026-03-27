% Contains a division by zero error resulting in a bad value
% The bad value should be propagated onwards
variable_define(recovery, six, val(int, 6)).
variable_define(recovery, two, val(int, 2)).
variable_define(recovery, add_three_twos, operation(add, (variable(two),(variable(two),(variable(two),()))))).
variable_define(recovery, six_minus_six, operation(sub, (variable(six),(variable(add_three_twos),())))).
variable_define(recovery, div_bad, operation(int_div, (variable(six),(variable(six_minus_six),())))).
variable_define(recovery, mult_bad, operation(mult, (variable(div_bad),(variable(two),())))).
variable_define(recovery, lt_bad, operation(lt, (variable(mult_bad),(variable(two),())))).

% Use the bad value to create conjunctions
% the false case should be recoverable since the value of bad doesn't affect the outcome.
variable_define(recovery, conj_bad, operation(conj, (variable(lt_bad),(val(bool,true),())))).
variable_define(recovery, conj_recovered, operation(conj, (variable(lt_bad),(val(bool,false),())))).

% The same for disjunctions
variable_define(recovery, disj_bad, operation(disj, (variable(lt_bad),(val(bool,false),())))).
variable_define(recovery, disj_recovered, operation(disj, (variable(lt_bad),(val(bool,true),())))).

% Operator `pow` is recoverable when exponent is 0.
variable_define(recovery, pow_bad, operation(pow, (variable(div_bad),(val(int,3),())))).
variable_define(recovery, pow_recovered, operation(pow, (variable(div_bad),(val(int,0),())))).

% Operator `limp` is recoverable when antecedent is false or consequent is true, because the bad value won't affect the outcome.
variable_define(recovery, limp_bad, operation(limp, (val(bool,true),(variable(lt_bad),())))).
variable_define(recovery, limp_bad_also, operation(limp, (variable(lt_bad),(val(bool,false),())))).
variable_define(recovery, limp_recovered, operation(limp, (val(bool,false),(variable(lt_bad),())))).
variable_define(recovery, limp_recovered_also, operation(limp, (variable(lt_bad),(val(bool,true),())))).

% Operator `ite` is recoverable when condition is evaluated such that the return value doesn't depend on the bad value.
variable_define(recovery, ite_bad, operation(ite, (variable(lt_bad),(val(int,1),(val(int,2),()))))).
variable_define(recovery, ite_recovered, operation(ite, (val(bool,false),(variable(lt_bad),(val(int,2),()))))).

% Operator `if` is recoverable when condition is false, because the branch with the bad value won't be taken.
variable_define(recovery, if_bad, operation(if, (variable(lt_bad),(val(int,1),())))).
variable_define(recovery, if_bad_also, operation(if, (val(bool,true),(variable(lt_bad),())))).
variable_define(recovery, if_recovered, operation(if, (val(bool,false),(variable(lt_bad),())))).

% Operator `default` is recoverable if the default value is bad but not taken.
variable_define(recovery, default_bad, operation(default, (variable(lt_bad),(val(int,1),())))).
variable_define(recovery, default_bad_also, operation(default, (val(none,none),(variable(lt_bad),())))).
variable_define(recovery, default_recovered, operation(default, (val(int,1),(variable(lt_bad),())))).