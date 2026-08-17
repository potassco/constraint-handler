phase_request(constantFolding,false).

evaluate(leqv,(val(bool,true),(bad,()))).
evaluate(leqv,(val(bool,false),(bad,()))).
evaluate(leqv,(bad,(bad,()))).
evaluate(lxor,(val(bool,true),(bad,()))).
evaluate(lxor,(val(bool,false),(bad,()))).
evaluate(lxor,(bad,(bad,()))).
