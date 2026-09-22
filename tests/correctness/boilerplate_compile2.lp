#script (python)
import constraint_handler

def main(ctrl):
    constraint_handler.add_to_control(ctrl, engine=constraint_handler.engine.compile2)
    ctrl.ground()
    ctrl.solve()
#end.
