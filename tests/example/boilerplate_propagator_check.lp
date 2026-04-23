defaultEngine(propagator).

#script (python)
import constraint_handler

def main(ctrl):
    constraint_handler.add_to_control(ctrl,propagator_check_only=True)
    ctrl.ground()
    ctrl.solve()
#end.
