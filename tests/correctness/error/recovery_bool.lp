% Contains a division by zero error resulting in a bad value
% The bad value should be propagated onwards
variable_define(two,val(int,2)).
variable_define(add_three_twos,operation(add,(variable(two),(variable(two),(variable(two),()))))).
variable_define(six_minus_six,operation(sub,(val(int,6),(variable(add_three_twos),())))).
variable_define(div_bad,operation(int_div,(val(int,7),(variable(six_minus_six),())))).
variable_define(lt_bad,operation(lt,(variable(div_bad),(variable(two),())))).

% Use the bad value to create conjunctions
% the false case should be recoverable since the value of bad doesn't affect the outcome.
variable_define(conj_bad,operation(conj,(variable(lt_bad),(val(bool,true),())))).
variable_define(conj_recovered,operation(conj,(variable(lt_bad),(val(bool,false),())))).

% The same for disjunctions
variable_define(disj_bad,operation(disj,(variable(lt_bad),(val(bool,false),())))).
variable_define(disj_recovered,operation(disj,(variable(lt_bad),(val(bool,true),())))).

% Operator `limp` is recoverable when antecedent is false or consequent is true, because the bad value won't affect the outcome.
variable_define(limp_bad,operation(limp,(val(bool,true),(variable(lt_bad),())))).
variable_define(limp_bad_also,operation(limp,(variable(lt_bad),(val(bool,false),())))).
variable_define(limp_recovered,operation(limp,(val(bool,false),(variable(lt_bad),())))).
variable_define(limp_recovered_also,operation(limp,(variable(lt_bad),(val(bool,true),())))).

% Operator `ite` is recoverable when condition is evaluated such that the return value doesn't depend on the bad value.
variable_define(ite_bad,operation(ite,(variable(lt_bad),(val(int,1),(val(int,2),()))))).
variable_define(ite_recovered,operation(ite,(val(bool,false),(variable(lt_bad),(val(int,2),()))))).
