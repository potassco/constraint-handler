#script (python)
import clingo
import constraint_handler as ch

def on_model(m):
    print(m)
    val = clingo.Function
    pyValue = ch.schemas.atom.Value(clingo.Function("y"),ch.schemas.expression.Val(ch.schemas.expression.BaseType.int,30))
    assert m.contains(ch.myClorm.pytocl(pyValue))

def main(ctrl):
    ch.add_to_control(ctrl)
    ctrl.add(
        "base",
        [],
        """
        variable_define(x,val(int,20)).
        variable_define(y,operation(add,(variable(x),(val(int,10),())))).
        #show value/2.
        """,
    )
    ctrl.ground()
    ctrl.solve(on_model=on_model)
    


#end.
