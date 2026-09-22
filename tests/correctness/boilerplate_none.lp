#script (python)
import constraint_handler

def main(ctrl):
    constraint_handler.add_to_control(ctrl, engine=constraint_handler.engine.none)
    ctrl.ground()
    ctrl.solve()
#end.
