#const int_domain_size = 17.


variable_declare(x,fromFacts).
variable_domain(x,val(int,1..int_domain_size)).

variable_define(y,operation(add,(variable(x),(val(int,1),())))).

ensure(max_domain_value,operation(eq,(variable(y),(val(int,int_domain_size+1),())))).

defaultEngine(propagator).

#script (python)
import constraint_handler

def main(ctrl):
    constraint_handler.add_to_control(ctrl,propagator_check_only=True)
    ctrl.ground()
    ctrl.solve()
#end.
