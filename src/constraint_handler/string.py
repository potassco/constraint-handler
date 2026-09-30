import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.operators as operators
import constraint_handler.schemas.result as result
import constraint_handler.schemas.warning as warning

NO_ERRORS: tuple[tuple[warning.Kind, str], ...] = ()


def evaluate_operator(o, args) -> result.EvalResult:
    match o:
        case operators.StringOperator.length:
            if len(args) != 1:
                return result.EvalResult(
                    expression.Bad.bad,
                    (
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            f"len takes one argument ({len(args)} were given)",
                        ),
                    ),
                )
            return result.EvalResult(len(args[0]), NO_ERRORS)
        case operators.StringOperator.concat:
            return result.EvalResult("".join(args), NO_ERRORS)
        case _:
            return result.EvalResult(
                expression.Bad.bad,
                ((warning.Expression(warning.ExpressionWarning.notImplemented), f"string operator {o}"),),
            )
