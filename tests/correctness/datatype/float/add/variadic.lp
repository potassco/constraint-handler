phase_request(constantFolding,false).

evaluate(add,()).
evaluate(add,(val(float,float("1.5")),())).
evaluate(add,(val(float,float("3.0")),(val(float,float("1.25")),(val(float,float("2.5")),())))).
evaluate(add,(val(int,2),(val(float,float("1.25")),(val(float,float("2.5")),())))).
