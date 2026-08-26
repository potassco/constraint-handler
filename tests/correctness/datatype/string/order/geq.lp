phase_request(constantFolding,false).

evaluate(geq,(val(string,"aa"),(val(string,"aa"),()))).
evaluate(geq,(val(string,"aa"),(val(string,"ab"),()))).
evaluate(geq,(val(string,"ab"),(val(string,"aa"),()))).
