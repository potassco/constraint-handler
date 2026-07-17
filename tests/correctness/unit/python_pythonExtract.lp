variable_declare(int_case,fromFacts).
variable_domain(int_case,val(int,3)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

variable_define(pool,operation(set_make,(val(int,1),(val(int,2),())))).

evaluate(pythonExtract("tmp=2","tmp"),()).
evaluate(pythonExtract("tmp=lhs*rhs","tmp+rhs"),((val(string,"lhs"),val(int,3)),((val(string,"rhs"),val(int,4)),()))).
evaluate(pythonExtract("tmp=raw","tmp"),((val(string,"raw"),variable(int_case)),())).
evaluate(pythonExtract("tmp=raw","tmp"),((val(string,"raw"),variable(none_case)),())).
evaluate(pythonExtract("tmp=raw","tmp"),((val(string,"raw"),variable(bad_case)),())).
evaluate(pythonExtract("present=pool.__contains__(2)","present"),((val(string,"pool"),variable(pool)),())).
evaluate(pythonExtract("lhs=lhs+2","lhs==5"),((val(string,"lhs"),val(int,3)),())).

#show evaluated/3.
