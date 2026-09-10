phase_request(wf_check,false).
variable_define(add_one,lambda((n,()),add(variable(n),1))).
variable_define(lambda_result,operation(variable(add_one),(2,()))).
