phase_request(constantFolding,false).

evaluate(concat,(val(string,"ab"),(val(string,"c"),()))).
evaluate(concat,(val(string,""),(val(string,"c"),()))).
evaluate(concat,(val(string,"ab"),(val(string,""),()))).
