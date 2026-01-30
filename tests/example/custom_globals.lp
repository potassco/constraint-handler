%% flooring(input: "x", output: "y"):
%%     y := math.floor(x)
execution_declare(dummy,flooring,STMT,("x",()),("y",())) :-
    STMT = statement_python("y = myths.floor(x)").
variable_define(dummy,execution_input(flooring,"x"),val(float,float("10.5"))).
execution_run(dummy,flooring).

variable_define(dummy,yep,operation(python("myths.floor"),(val(float,float("3.333")),()))).

variable_define(dummy,nope,operation(default,(operation(python("math.floor"),(val(float,float("3.333")),())),(val(int,5),())))).

main_solverIdentifier(3).

execution_declare(dummy,empty,STMT,(),("y",())) :-
    STMT = statement_python("y = '5'").
execution_run(dummy,empty).

#show value/2.
#show warning/1.
#show warning/3.

#script (python)

import constraint_handler.evaluator as evaluator

if "math" in evaluator._shared_environment:
    del evaluator._shared_environment["math"]
evaluator._solver_environment[3] = { "myths": __import__("math") }

#end.
