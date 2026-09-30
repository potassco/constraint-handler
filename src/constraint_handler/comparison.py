import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.operators as operators
import constraint_handler.schemas.result as result
import constraint_handler.schemas.warning as warning

NO_ERRORS: tuple[tuple[warning.Kind, str], ...] = ()


def evaluate_operator(o, args) -> result.EvalResult:
    match o:
        case operators.ComparisonOperator.eq:
            if len(args) != 2:
                return result.EvalResult(
                    expression.Bad.bad,
                    (
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            f"eq takes two arguments, not {args}",
                        ),
                    ),
                )
            return result.EvalResult(args[0] == args[1], NO_ERRORS)
        case operators.ComparisonOperator.neq:
            if len(args) != 2:
                return result.EvalResult(
                    expression.Bad.bad,
                    (
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            f"eq takes two arguments, not {args}",
                        ),
                    ),
                )
            return result.EvalResult(args[0] != args[1], NO_ERRORS)
        case operators.ComparisonOperator.max:
            assert len(args)  # TODO
            return result.EvalResult(max(args), NO_ERRORS)
        case operators.ComparisonOperator.min:
            assert len(args)
            return result.EvalResult(min(args), NO_ERRORS)
        case _:
            return result.EvalResult(
                expression.Bad.bad,
                ((warning.Expression(warning.ExpressionWarning.notImplemented), f"comparison operator {o}"),),
            )
