%#show direct_query/1.
%#show value/3.
variable_define(example1_pi,pi,val(float,float("3.14159"))).
variable_define(example1_y,y,
       operation(mult,
                    (operation(add,(variable(pi),(val(int,2),()))),
                    (val(float,float("3.14159")),())))).
%ensure(example_check1,
%       operation(leq,
%                    (operation(add,(val(float,float("3.14159")),
%                                        (val(float,float(3)),()))),
%                    (val(float,float(10)),())))).
ensure(example_check1,
       operation(leq,
                    (operation(add,(val(int,3),
                                        (val(int,3),()))),
                    (val(int,10),())))).
%ensure(example_check2,
%       operation(leq,
%                    (operation(div,(variable(y),(val(int,3),()))),
%                    (val(int,15),())))).
