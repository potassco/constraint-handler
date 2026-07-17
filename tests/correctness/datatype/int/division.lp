variable_define(two,val(int,2)).
variable_define(ten,val(int,10)).
variable_define(divtwoten,operation(int_div,(variable(two),(variable(ten),())))).
variable_define(divtentwo,operation(int_div,(variable(ten),(variable(two),())))).