phase_request(constantFolding,false).

evaluate(leq,(val(string,"aa"),(val(string,"aa"),()))).
evaluate(leq,(val(string,"aa"),(val(string,"ab"),()))).
evaluate(leq,(val(string,"ab"),(val(string,"aa"),()))).
