import constraint_handler.schemas.atom as atom
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.operators as operators
import constraint_handler.schemas.warning as warning

NO_ERRORS: tuple[tuple[warning.Kind, str], ...] = ()


def evaluate_operator(o, args) -> atom.EvalResult:
    match o:
        case operators.StringOperator.length:
            if len(args) != 1:
                return atom.EvalResult(
                    expression.Bad.bad,
                    (
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            f"len takes one argument ({len(args)} were given)",
                        ),
                    ),
                )
            return atom.EvalResult(len(args[0]), NO_ERRORS)
        case operators.StringOperator.concat:
            return atom.EvalResult("".join(args), NO_ERRORS)
        case _:
            return atom.EvalResult(
                expression.Bad.bad,
                ((warning.Expression(warning.ExpressionWarning.notImplemented), f"string operator {o}"),),
            )
