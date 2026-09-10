import constraint_handler.schemas.atom as atom
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.operators as operators
import constraint_handler.schemas.warning as warning

NO_ERRORS: tuple[tuple[warning.Kind, str], ...] = ()


def evaluate_operator(o, args) -> atom.EvalResult:
    match o:
        case operators.ConditionalOperator.getOrElse:
            return atom.EvalResult(args[0] if args[0] is not None else args[1], NO_ERRORS)
        case operators.ConditionalOperator.IF:
            if args[0] is expression.Bad.bad:
                return atom.EvalResult(expression.Bad.bad, NO_ERRORS)
            if args[0] is True:
                return atom.EvalResult(args[1], NO_ERRORS)
            return atom.EvalResult(None, NO_ERRORS)
        case operators.ConditionalOperator.ite:
            assert len(args) == 3
            if args[0] is None:
                return atom.EvalResult(None, NO_ERRORS)
            if args[0] is expression.Bad.bad:
                return atom.EvalResult(expression.Bad.bad, NO_ERRORS)
            return atom.EvalResult(args[1] if args[0] else args[2], NO_ERRORS)
        case operators.ConditionalOperator.hasValue:
            return atom.EvalResult(args[0] is not None, NO_ERRORS)
        case _:
            return atom.EvalResult(
                expression.Bad.bad,
                ((warning.Expression(warning.ExpressionWarning.notImplemented), f"conditional operator {o}"),),
            )
