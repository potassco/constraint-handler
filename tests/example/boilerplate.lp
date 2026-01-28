#script (python)
import constraint_handler as ch

def main(ctrl):
    ch.add_to_control(ctrl)
    ctrl.ground()
    ctrl.solve()
#end.
