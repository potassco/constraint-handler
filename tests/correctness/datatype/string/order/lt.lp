phase_request(constantFolding,false).

evaluate(lt,(val(string,"aa"),(val(string,"aa"),()))).
evaluate(lt,(val(string,"aa"),(val(string,"ab"),()))).
evaluate(lt,(val(string,"ab"),(val(string,"aa"),()))).
