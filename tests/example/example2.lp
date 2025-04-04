#include "includeAll.lp".

%#show expression/1.
%#show value/3.
assign(example1_pi,pi,constant(float("3.14159"))).
assign(example1_y,y,
       operation(mult,
                    (operation(add,(variable(pi),(constant(int(2)),()))),
                    (constant(float("3.14159")),())))).
%ensure(example_check1,
%       operation(leq,
%                    (operation(add,(constant(float("3.14159")),
%                                        (constant(float(3)),()))),
%                    (constant(float(10)),())))).
ensure(example_check1,
       operation(leq,
                    (operation(add,(constant(int(3)),
                                        (constant(int(3)),()))),
                    (constant(int(10)),())))).
%ensure(example_check2,
%       operation(leq,
%                    (operation(div,(variable(y),(constant(int(3)),()))),
%                    (constant(int(15)),())))).
