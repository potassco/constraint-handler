defaultEngine(propagator).

#script (python)
import constraint_handler

def main(ctrl):
    constraint_handler.add_to_control(ctrl)
    ctrl.ground()
    ctrl.solve()
#end.
