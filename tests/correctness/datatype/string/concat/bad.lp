phase_request(constantFolding,false).

evaluate(concat,(bad,(val(string,"c"),()))).
evaluate(concat,(val(string,"ab"),(bad,()))).
evaluate(concat,(bad,(bad,()))).
