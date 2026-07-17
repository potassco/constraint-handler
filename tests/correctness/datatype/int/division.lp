%%% integer division checks moved from comparison notes
%%% 2//10==0     10//2==5
variable_define(two,val(int,2)).
variable_define(ten,val(int,10)).
variable_define(divtwoten,operation(int_div,(variable(two),(variable(ten),())))).
variable_define(divtentwo,operation(int_div,(variable(ten),(variable(two),())))).