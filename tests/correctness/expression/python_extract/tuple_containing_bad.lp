phase_request(constantFolding,false).
phase_request(safe,false).

evaluate(operation(pythonExtract("pass","len(x)"),((val(string,"x"),(bad,val(int,1))),()))).
