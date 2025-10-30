defaultEngine(propagator).

#script (python)

import clingo
import constraint_handler.propagator as prop

def main(prg):

    propagator = prop.ConstraintHandlerPropagator()
    prg.register_propagator(propagator)
    prg.ground()
    prg.solve(on_model=propagator.on_model)

#end.
