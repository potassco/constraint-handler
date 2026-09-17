import constraint_handler.schemas.operators as operators
import constraint_handler.schemas.result as result
import constraint_handler.schemas.warning as warning
import constraint_handler.utils.common as common
import constraint_handler.utils.errors as errors

NO_ERRORS: tuple[tuple[warning.Kind, str], ...] = ()


def fold(f, s, start):
    # print("fold", f, s, start)
    accu = start
    for e in s:
        accu = f(e, accu)
    return accu


def evaluate_operator(o, args, apply_operator=None) -> result.EvalResult:
    match o:
        case operators.SetOperator.cardinality:
            if len(args) != 1:
                return result.EvalResult(
                    common.Bad.bad,
                    (
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            str(errors.incorrect_arity_error(o, 1, len(args))),
                        ),
                    ),
                )
            if args[0] == common.Bad.bad:
                return result.EvalResult(common.Bad.bad, NO_ERRORS)
            return result.EvalResult(len(args[0]), NO_ERRORS)
        case operators.SetOperator.set_make:
            return result.EvalResult(frozenset(args), NO_ERRORS)
        case operators.SetOperator.set_isin:
            if len(args) != 2:
                return result.EvalResult(
                    common.Bad.bad,
                    (
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            str(errors.incorrect_arity_error(o, 2, len(args))),
                        ),
                    ),
                )
            if common.Bad.bad in args:
                return result.EvalResult(common.Bad.bad, NO_ERRORS)
            return result.EvalResult(args[0] in args[1], NO_ERRORS)
        case operators.SetOperator.set_notin:
            if len(args) != 2:
                return result.EvalResult(
                    common.Bad.bad,
                    (
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            str(errors.incorrect_arity_error(o, 2, len(args))),
                        ),
                    ),
                )
            if args[1] == common.Bad.bad:
                return result.EvalResult(common.Bad.bad, NO_ERRORS)
            return result.EvalResult(args[0] not in args[1], NO_ERRORS)
        case operators.SetOperator.union:
            if common.Bad.bad in args:
                return result.EvalResult(common.Bad.bad, NO_ERRORS)
            return result.EvalResult(frozenset().union(*args), NO_ERRORS)
        case operators.SetOperator.inter:
            if len(args) < 1:
                return result.EvalResult(
                    common.Bad.bad,
                    (
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            str(errors.incorrect_arity_error(o, "at least 1", len(args))),
                        ),
                    ),
                )
            if common.Bad.bad in args:
                return result.EvalResult(common.Bad.bad, NO_ERRORS)
            return result.EvalResult(frozenset(args[0].intersection(*args[1:])), NO_ERRORS)
        case operators.SetOperator.diff:
            if len(args) != 2:
                return result.EvalResult(
                    common.Bad.bad,
                    (
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            str(errors.incorrect_arity_error(o, 2, len(args))),
                        ),
                    ),
                )
            if common.Bad.bad in args:
                return result.EvalResult(common.Bad.bad, NO_ERRORS)
            return result.EvalResult(frozenset(args[0].difference(args[1])), NO_ERRORS)
        case operators.SetOperator.subset:
            if len(args) != 2:
                return result.EvalResult(
                    common.Bad.bad,
                    (
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            str(errors.incorrect_arity_error(o, 2, len(args))),
                        ),
                    ),
                )
            if common.Bad.bad in args:
                return result.EvalResult(common.Bad.bad, NO_ERRORS)
            return result.EvalResult(args[0].issubset(args[1]), NO_ERRORS)
        case operators.SetOperator.set_fold:
            if len(args) != 3:
                return result.EvalResult(
                    common.Bad.bad,
                    (
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            str(errors.incorrect_arity_error(o, 3, len(args))),
                        ),
                    ),
                )
            if args[1] == common.Bad.bad or args[2] == common.Bad.bad:
                return result.EvalResult(common.Bad.bad, NO_ERRORS)
            if apply_operator is None:
                return result.EvalResult(
                    common.Bad.bad,
                    ((warning.Expression(warning.ExpressionWarning.notImplemented), "set_fold missing callback"),),
                )
            fold_errors = []

            def step(*aaa):
                applied = apply_operator(args[0], aaa)
                fold_errors.extend(applied.errors)
                return applied.value

            return result.EvalResult(fold(step, args[1], args[2]), tuple(fold_errors))
        case _:
            return result.EvalResult(
                common.Bad.bad,
                ((warning.Expression(warning.ExpressionWarning.notImplemented), f"set.operator {o}"),),
            )
