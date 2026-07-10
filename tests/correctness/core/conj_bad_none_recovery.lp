variable_define(two,val(int,2)).
variable_define(add_three_twos,operation(add,(variable(two),(variable(two),(variable(two),()))))).
variable_define(six_minus_six,operation(sub,(val(int,6),(variable(add_three_twos),())))).
variable_define(div_bad,operation(int_div,(val(int,7),(variable(six_minus_six),())))).
variable_define(lt_bad,operation(lt,(variable(div_bad),(variable(two),())))).

evaluate(conj,(variable(lt_bad),(val(none,none),()))).

#show evaluated/3.
