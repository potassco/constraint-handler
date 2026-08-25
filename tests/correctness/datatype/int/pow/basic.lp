phase_request(constantFolding,false).

evaluate(pow,(val(int,2),(val(int,3),()))).
evaluate(pow,(val(int,-3),(val(int,2),()))).
evaluate(pow,(val(int,-3),(val(int,5),()))).
evaluate(pow,(val(int,4),(val(int,0),()))).
evaluate(pow,(val(int,-5),(val(int,0),()))).
