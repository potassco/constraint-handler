#include "includeAll.lp".

1 { assign(example1_x,x,constant(int(0..5))) } 1.
%1 { assign(example1_x,x,constant(float("0";"3";"5"))) } 1.

assign(example1_pi,pi,constant(float("3.14159"))).
assign(example1_y,y,
       operation(mult,
                (operation(add,(variable(x),(constant(int(2)),()))),
                (variable(pi),())))).
%ensure(example_check1,
%       operation(geq,
%                (operation(div,(variable(y),(constant(float("3")),()))),
%                (constant(float("10")),())))).
%ensure(example_check2,
%       operation(leq,
%                (operation(div,(variable(y),(constant(float("3")),()))),
%                (constant(float("15")),())))).

%#show value/3.
%#show expression/1.
