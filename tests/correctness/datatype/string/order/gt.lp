phase_request(constantFolding,false).

evaluate(gt,(val(string,"aa"),(val(string,"aa"),()))).
evaluate(gt,(val(string,"aa"),(val(string,"ab"),()))).
evaluate(gt,(val(string,"ab"),(val(string,"aa"),()))).
