phase_request(type_check,true).

variable_declare(lhs,fromFacts).
variable_domain(lhs,val(int,2)).

variable_declare(rhs,fromFacts).
variable_domain(rhs,val(int,3)).

variable_define(sum_expr,operation(pythonExtract("tmp = lhs + rhs","tmp"),((val(string,"lhs"),variable(lhs)),((val(string,"rhs"),variable(rhs)),())))).
variable_define(cmp_expr,operation(pythonExtract("tmp = lhs + rhs","tmp > 0"),((val(string,"lhs"),variable(lhs)),((val(string,"rhs"),variable(rhs)),())))).
