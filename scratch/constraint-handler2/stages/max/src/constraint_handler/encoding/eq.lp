#script (python)
from clingo.symbol import Function, Number, SymbolType, Tuple_


def convert(lib, value):
    """Convert an integral real to its integer term when representable."""
    number = float(value.string)
    if number.is_integer() and -(2**31) <= number < 2**31:
        return Function(lib, "integer", [Number(lib, int(number))])
    return Function(lib, "real", [value])


def tuple_key(lib, value):
    """Traverse tuples, converting only their real members."""
    if value.type == SymbolType.Tuple:
        return Tuple_(lib, [tuple_key(lib, item) for item in value.arguments])
    if value.type == SymbolType.Function:
        if value.name == "real":
            return convert(lib, value.arguments[0])
        if value.name == "tuple":
            return Function(lib, "tuple", [tuple_key(lib, value.arguments[0])])
    return value
#end.

equality_operands(Id, Op, Left, Right) :-
    native_expression(Id, operation(Op, (Left, Right))), Op = (eq; neq).

equality_input(Arg) :-
    equality_operands(_, _, Left, Right), Arg = (Left; Right).
equality_defined(Arg) :- equality_input(Arg), value(Arg, _).
equality_set(Arg) :- equality_input(Arg), value(Arg, set).

equality_value(Value) :-
    equality_input(Arg), value(Arg, Value), Value != set, Value != tuple.
equality_value(Member) :-
    equality_set(Arg), set_value(Arg, Member).
equality_real(real(Real)) :- equality_value(real(Real)).
equality_tuple(tuple(Items)) :- equality_value(tuple(Items)).
equality_key(Value, Value) :-
    equality_value(Value), not equality_real(Value), not equality_tuple(Value).
equality_key(real(Real), @convert(Real)) :- equality_value(real(Real)).
equality_key(tuple(Items), tuple(@tuple_key(Items))) :-
    equality_value(tuple(Items)).

equality_scalar_key(Arg, Key) :-
    equality_input(Arg), value(Arg, Value), equality_key(Value, Key).
equality_set_key(Arg, Key) :-
    equality_set(Arg), set_value(Arg, Member), equality_key(Member, Key).

equality_scalar(Id, Op) :-
    equality_operands(Id, Op, Left, Right),
    equality_defined(Left), equality_defined(Right), not equality_set(Left),
    not equality_tuple_subject(Left).
equality_scalar(Id, Op) :-
    equality_operands(Id, Op, Left, Right),
    equality_defined(Left), equality_defined(Right), not equality_set(Right),
    not equality_tuple_subject(Right).

equality_match(Id) :-
    equality_operands(Id, _, Left, Right),
    equality_scalar_key(Left, Key), equality_scalar_key(Right, Key).

value(Id, boolean(true)) :- equality_scalar(Id, eq), equality_match(Id).
value(Id, boolean(false)) :- equality_scalar(Id, eq), not equality_match(Id).
value(Id, boolean(false)) :- equality_scalar(Id, neq), equality_match(Id).
value(Id, boolean(true)) :- equality_scalar(Id, neq), not equality_match(Id).