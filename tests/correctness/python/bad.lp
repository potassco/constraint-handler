variable_define(div_bad,operation(python("lambda x: 1 / x"),(val(int,0),()))).
variable_define(missing_global,operation(python("missing_callable"),(val(int,1),()))).

#show value/2.
