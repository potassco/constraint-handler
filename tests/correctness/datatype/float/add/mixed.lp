phase_request(constantFolding,false).

evaluate(add,(val(float,float("1.5")),(val(int,2),()))).
evaluate(add,(val(int,2),(val(float,float("1.5")),()))).
