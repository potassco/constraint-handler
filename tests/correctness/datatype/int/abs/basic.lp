phase_request(constantFolding,false).

evaluate(abs,(val(int,-3),())).
evaluate(abs,(val(int,2),())).
evaluate(abs,(operation(sub,(val(int,2),(val(int,10),()))),())).
evaluate(abs,(operation(sub,(val(int,10),(val(int,2),()))),())).
