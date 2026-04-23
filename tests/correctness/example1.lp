variable_declare(x,fromFacts).
variable_domain(x,val(int,0..5)).
%1 { variable_define(x,val(float,float("0";"3";"5"))) } 1.

variable_define(pi,val(float,float("3.14159"))).
variable_define(y,
       operation(mult,
                (operation(add,(variable(x),(val(int,2),()))),
                (variable(pi),())))).
%ensure(operation(geq,
%                (operation(int_div,(variable(y),(val(float,float("3")),()))),
%                (val(float,float("10")),())))).
%ensure(operation(leq,
%                (operation(int_div,(variable(y),(val(float,float("3")),()))),
%                (val(float,float("15")),())))).

%#show value/3.
%#show direct_query/1.
