#include "includeAll.lp".

variable_declare(example1_x,x,fromFacts).
variable_domain(x,val(int,0..5)).
%1 { variable_define(example1_x,x,val(float,float("0";"3";"5"))) } 1.

variable_define(example1_pi,pi,val(float,float("3.14159"))).
variable_define(example1_y,y,
       operation(mult,
                (operation(add,(variable(x),(val(int,2),()))),
                (variable(pi),())))).
%ensure(example_check1,
%       operation(geq,
%                (operation(div,(variable(y),(val(float,float("3")),()))),
%                (val(float,float("10")),())))).
%ensure(example_check2,
%       operation(leq,
%                (operation(div,(variable(y),(val(float,float("3")),()))),
%                (val(float,float("15")),())))).

%#show value/3.
%#show direct_query/1.
