import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.operators as operators
import constraint_handler.schemas.result as result
import constraint_handler.schemas.warning as warning

NO_ERRORS: tuple[tuple[warning.Kind, str], ...] = ()


def evaluate_operator(o, args) -> result.EvalResult:
    match o:
        case operators.ConditionalOperator.getOrElse:
            return result.EvalResult(args[0] if args[0] is not None else args[1], NO_ERRORS)
        case operators.ConditionalOperator.IF:
            if args[0] is expression.Bad.bad:
                return result.EvalResult(expression.Bad.bad, NO_ERRORS)
            if args[0] is True:
                return result.EvalResult(args[1], NO_ERRORS)
            return result.EvalResult(None, NO_ERRORS)
        case operators.ConditionalOperator.ite:
            assert len(args) == 3
            if args[0] is None:
                return result.EvalResult(None, NO_ERRORS)
            if args[0] is expression.Bad.bad:
                return result.EvalResult(expression.Bad.bad, NO_ERRORS)
            return result.EvalResult(args[1] if args[0] else args[2], NO_ERRORS)
        case operators.ConditionalOperator.hasValue:
            return result.EvalResult(args[0] is not None, NO_ERRORS)
        case _:
            return result.EvalResult(
                expression.Bad.bad,
                ((warning.Expression(warning.ExpressionWarning.notImplemented), f"conditional operator {o}"),),
            )
