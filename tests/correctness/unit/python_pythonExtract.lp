phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(int,3)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(pythonExtract("tmp=raw","tmp"),((val(string,"raw"),variable(x)),())).


variable_define(pool,operation(set_make,(val(int,1),(val(int,2),())))).

evaluate(pythonExtract("tmp=lhs*rhs","tmp+rhs"),((val(string,"lhs"),val(int,3)),((val(string,"rhs"),val(int,4)),()))).
evaluate(pythonExtract("tmp=raw","tmp"),((val(string,"raw"),val(int,3)),())).
evaluate(pythonExtract("tmp=raw","tmp"),((val(string,"raw"),val(none,none)),())).
evaluate(pythonExtract("tmp=raw","tmp"),((val(string,"raw"),bad),())).
evaluate(pythonExtract("present=pool.__contains__(2)","present"),((val(string,"pool"),variable(pool)),())).
evaluate(pythonExtract("lhs=lhs+2","lhs==5"),((val(string,"lhs"),val(int,3)),())).
