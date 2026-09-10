import constraint_handler.schemas.atom as atom
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.operators as operators
import constraint_handler.schemas.warning as warning

NO_ERRORS: tuple[tuple[warning.Kind, str], ...] = ()


def evaluate_operator(o, args) -> atom.EvalResult:
    match o:
        case operators.ComparisonOperator.eq:
            if len(args) != 2:
                return atom.EvalResult(
                    expression.Bad.bad,
                    (
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            f"eq takes two arguments, not {args}",
                        ),
                    ),
                )
            return atom.EvalResult(args[0] == args[1], NO_ERRORS)
        case operators.ComparisonOperator.neq:
            if len(args) != 2:
                return atom.EvalResult(
                    expression.Bad.bad,
                    (
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            f"eq takes two arguments, not {args}",
                        ),
                    ),
                )
            return atom.EvalResult(args[0] != args[1], NO_ERRORS)
        case operators.ComparisonOperator.max:
            assert len(args)  # TODO
            return atom.EvalResult(max(args), NO_ERRORS)
        case operators.ComparisonOperator.min:
            assert len(args)
            return atom.EvalResult(min(args), NO_ERRORS)
        case _:
            return atom.EvalResult(
                expression.Bad.bad,
                ((warning.Expression(warning.ExpressionWarning.notImplemented), f"comparison operator {o}"),),
            )
