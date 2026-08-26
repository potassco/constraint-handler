phase_request(constantFolding,false).

evaluate(add,(val(int,2),(val(int,3),()))).
evaluate(add,(val(int,5),(val(int,5),()))).
evaluate(add,(val(int,2),(val(bool,true),()))).
evaluate(add,(val(int,2),(val(bool,false),()))).
