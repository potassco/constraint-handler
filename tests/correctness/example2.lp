%#show direct_query/1.
%#show value/3.
variable_define(pi,val(float,float("3.14159"))).
variable_define(y,
       operation(mult,
                    (operation(add,(variable(pi),(val(int,2),()))),
                    (val(float,float("3.14159")),())))).
%ensure(operation(leq,
%                    (operation(add,(val(float,float("3.14159")),
%                                        (val(float,float(3)),()))),
%                    (val(float,float(10)),())))).
ensure(operation(leq,
                    (operation(add,(val(int,3),
                                        (val(int,3),()))),
                    (val(int,10),())))).
%ensure(operation(leq,
%                    (operation(int_div,(variable(y),(val(int,3),()))),
%                    (val(int,15),())))).
