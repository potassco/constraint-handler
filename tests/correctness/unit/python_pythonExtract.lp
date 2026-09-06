evaluate(operation(pythonExtract("tmp=lhs*rhs\nres=tmp+rhs","res"),((val(string,"lhs"),val(int,3)),((val(string,"rhs"),val(int,4)),())))).
evaluate(operation(pythonExtract("tmp=raw","tmp"),((val(string,"raw"),val(int,3)),()))).
evaluate(operation(pythonExtract("tmp=raw","tmp"),((val(string,"raw"),val(none,none)),()))).
evaluate(operation(pythonExtract("tmp=raw","tmp"),((val(string,"raw"),bad),()))).
evaluate(operation(pythonExtract("present=pool.__contains__(2)","present"),((val(string,"pool"),operation(set_make,(val(int,1),(val(int,2),())))),()))).
evaluate(operation(pythonExtract("lhs=lhs+2\nres=lhs==5","res"),((val(string,"lhs"),val(int,3)),()))).

variable_declare(x,fromFacts).
variable_domain(x,val(int,3)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(pythonExtract("tmp=raw","tmp"),((val(string,"raw"),variable(x)),()))).
