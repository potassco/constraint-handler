%%% power checks moved from comparison notes
%%% 2**10==1024     10**2==100
variable_define(two,val(int,2)).
variable_define(ten,val(int,10)).
variable_define(powtwoten,operation(pow,(variable(two),(variable(ten),())))).
variable_define(powtentwo,operation(pow,(variable(ten),(variable(two),())))).
