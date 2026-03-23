from typing import Any


def incorrect_arity_error(operator: Any, expected_arity: int | str, given_arity: int) -> TypeError:
    """
    Create a TypeError for incorrect operator arity.

    Args:
        operator: The operator that was called
        expected_arity: Expected number of arguments (int or string like "at least 1")
        given_arity: Actual number of arguments provided

    Returns:
        TypeError instance with appropriate message
    """
    operator_name = str(operator).split(".")[-1]
    if isinstance(expected_arity, int):
        arity_desc = f"exactly {expected_arity}"
        arg_word = "argument" if expected_arity == 1 else "arguments"
    else:
        arity_desc = str(expected_arity)
        arg_word = "arguments"

    given_word = "was given" if given_arity == 1 else "were given"

    return TypeError(f"{operator_name} takes {arity_desc} {arg_word} ({given_arity} {given_word})")
