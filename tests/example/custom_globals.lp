#include "includeAll.lp".



%% flooring(input: "x", output: "y"):
%%     y := math.floor(x)
execution_declare(dummy,flooring,STMT,("x",()),("y",())) :-
    STMT = python("y = myths.floor(x)",("x",()),("y",())).
assign(dummy,execution_input(flooring,"x"),val(float,float("10.5"))).
execution_run(dummy,flooring).
%assign(dummy,my_y,variable(execution_output(flooring,"y"))).

assign(dummy,yep,operation(python("myths.floor"),(val(float,float("3.333")),()))).

assign(dummy,nope,operation(default,(operation(python("math.floor"),(val(float,float("3.333")),())),(val(int,5),())))).

#show value/3.

#script (python)

ch_globals_dict = {"myths": __import__("math")}

#end.