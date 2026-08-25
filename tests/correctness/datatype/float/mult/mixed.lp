phase_request(constantFolding,false).

evaluate(mult,(val(float,float("1.5")),(val(int,2),()))).
evaluate(mult,(val(int,2),(val(float,float("1.5")),()))).
evaluate(mult,(val(float,float("1.5")),(val(int,3),()))).
evaluate(mult,(val(int,3),(val(float,float("1.5")),()))).
