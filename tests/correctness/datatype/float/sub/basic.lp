phase_request(constantFolding,false).

evaluate(sub,(val(float,float("2.5")),(val(int,2),()))).
evaluate(sub,(val(float,float("2.5")),(val(float,float("3.125")),()))).
evaluate(sub,(val(int,2),(val(float,float("3.125")),()))).
