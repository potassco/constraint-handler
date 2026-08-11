phase_request(constantFolding,false).

evaluate(pythonExtract("tmp=lhs*rhs\nres=tmp+rhs","res"),((val(string,"lhs"),val(int,3)),((val(string,"rhs"),val(int,4)),()))).
evaluate(pythonExtract("tmp=raw","tmp"),((val(string,"raw"),val(int,3)),())).
evaluate(pythonExtract("tmp=raw","tmp"),((val(string,"raw"),val(none,none)),())).
evaluate(pythonExtract("tmp=raw","tmp"),((val(string,"raw"),bad),())).
evaluate(pythonExtract("present=pool.__contains__(2)","present"),((val(string,"pool"),operation(set_make,(val(int,1),(val(int,2),())))),())).
evaluate(pythonExtract("lhs=lhs+2\nres=lhs==5","res"),((val(string,"lhs"),val(int,3)),())).

variable_declare(x,fromFacts).
variable_domain(x,val(int,3)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(pythonExtract("tmp=raw","tmp"),((val(string,"raw"),variable(x)),())).
