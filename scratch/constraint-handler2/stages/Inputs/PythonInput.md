## Information

This file describes the caller-facing Python interface and expression model for
adding input to a `ConstraintStore`. Input is declarative: variables are
declared and defined with expressions, rather than represented as executable
statements. A possible internal storage representation is described in
[InternalInput](InternalInput.md).

Operator meanings are shared across input formats; see
[Operator Semantics](../OperatorSemantics.md).

```python
from python_input import Operation, Operator, VariableRef

store = ConstraintStore()
store.choose_from_iterator(
    VariableRef("x"),
    (1, 2)
)
store.define(
    VariableRef("y"),
    Operation(
        Operator.add,
        (VariableRef("x"), 1),
    )
)
store.ensure(Operation(Operator.eq, (VariableRef("x"), 2)))
```

## ASP Format

## Python Datastructure

### Variables

```python
# A VariableRef stores the name of a variable used by an expression.
# For example, x in x + 2 is represented by VariableRef(x).
#
VariableRef(name: str)

```

### ConstraintStore Methods

```python
from collections.abc import Iterable

class ConstraintStore:
    # choose adds a single candidate expression to the variable's choices.
    #
    def choose(self, name: VariableRef, value: Expr, condition: Expr = expression.TRUE, label: str = LABEL_ANONYMOUS): ...

    # choose_from_iterator adds candidate expressions from an iterable to the variable's choices.
    # Syntactic sugar and equivalent to repeated calls to choose with each element.
    # Repeated calls extend one list of elements, retaining duplicates, conditions, and labels.
    #
    def choose_from_iterator(self, name: VariableRef, choices: Iterable[Expr] = (), condition: Expr = expression.TRUE, label: str = LABEL_ANONYMOUS): ...

    # define appends a labeled defining expression to a variable.
    # The definition is active only when condition holds.
    # Repeated calls retain all definitions, conditions, and labels.
    #
    def define(self, name: VariableRef, value: Expr, condition: Expr = expression.TRUE, label: str = LABEL_ANONYMOUS): ...

    # default_to defines a conditional default value with a priority.
    #
    def default_to(self, name: VariableRef, value: Expr, condition: Expr = expression.TRUE, priority: int = 0, label: str = LABEL_ANONYMOUS): ...

    # set_contain requires set variable name to contain value when condition holds.
    #
    def set_contain(self, name: VariableRef, value: Expr, condition: Expr = expression.TRUE, label: str = LABEL_ANONYMOUS): ...

    # set_contain_default_to defines a conditional default element for a set variable with a priority.
    #
    def set_contain_default_to(self, name: VariableRef, value: Expr, condition: Expr = expression.TRUE, priority: int = 0, label: str = LABEL_ANONYMOUS): ...

    # set_contain_choose lets set variable name choose whether to contain value.
    #
    def set_contain_choose(self, name: VariableRef, value: Expr, condition: Expr = expression.TRUE, label: str = LABEL_ANONYMOUS): ...

    # set_contain_choose_from_iterator adds candidate elements from an iterable to the set variable.
    # Syntactic sugar and equivalent to repeated calls to set_contain_choose with each element.
    #
    def set_contain_choose_from_iterator(self, name: VariableRef, choices: Iterable[Expr] = (), condition: Expr = expression.TRUE, label: str = LABEL_ANONYMOUS): ...

    # actual constraints
    # check(x/0 > 9). holds and ensure(x/0 > 9) does not hold
    def ensure(self, expr: Expr, label: str = LABEL_ANONYMOUS): ...
    def check(self, expr: Expr, label: str = LABEL_ANONYMOUS): ...

# Examples
from python_input import Operation, Operator, VariableRef

store.choose(VariableRef("a"), 42, label="input")
store.choose_from_iterator(VariableRef("x"), (1, 2), label="input")
store.define(VariableRef("x"), 2, label="input")
store.default_to(
    VariableRef("x"),
    0,
    Operation(Operator.eq, (VariableRef("x"), 1)),
    1,
    "defaults",
)
store.set_contain(VariableRef("s"), 42)
store.set_contain_default_to(
    VariableRef("s"),
    42,
    Operation(Operator.eq, (VariableRef("x"), 1)),
    1,
    "defaults",
)
store.set_contain_choose(VariableRef("s"), 42)
store.set_contain_choose_from_iterator(VariableRef("s"), (1, 2))


```

### Expressions

```python
# These expression types belong to the python_input namespace.
#
Expr = VariableRef | Value | Set | Tuple | Operation

# Scalar values use Python base types at the user-facing boundary.
#
Value = bool | float | int | str | None

# Collections are expression forms, not scalar values.
#
Set = frozenset[Expr]
Tuple = tuple[Expr, ...]

# Operation stores an operator and its argument expressions.
# For example, x + 2 is represented by Operation(Operator.add, (VariableRef("x"), 2)).
#
OperationArg = Expr | Lambda | Python
Operation(op: Operator, args: tuple[OperationArg, ...])
# Example: Operation(Operator.add, (VariableRef("x"), 2)).

# Lambda stores parameter names and an expression body.
#
Lambda(vars: tuple[VariableRef, ...], expr: Expr)
# Example: Lambda((VariableRef("x"),), Operation(Operator.add, (VariableRef("x"), 2))).

# Python stores trusted source evaluating to a deterministic, side-effect-free callable.
#
Python(fn: str)
# Example: Python("lambda x: math.sqrt(x)") accepts one python_eval argument.


# Operator lists all operator values accepted by Operation.
#
enum Operator {
    # Equality comparisons
    eq,
    neq,

    # String and generic value operations; length is shared by both categories
    concat,
    length,
    max,
    min,

    # Conditional operations
    get_or_else,
    if_,
    has_value,

    # Arithmetic and ordered comparisons
    abs,
    sqrt,
    cos,
    sin,
    tan,
    acos,
    asin,
    atan,
    minus,
    floor,
    ceil,
    add,
    sub,
    mult,
    linear_integer,
    linear_comparison,
    int_div,
    real_div,
    pow,
    leq,
    lt,
    geq,
    gt,
    real_from_int,
    int_from_real,

    # Boolean and three-valued logic
    conj,
    disj,
    ite,
    leqv,
    limp,
    lnot,
    lxor,
    snot,
    wnot,

    # Set construction and queries
    cardinality,
    set_make,
    set_isin,
    set_notin,
    union,
    inter,
    diff,
    subset,
    set_fold,

    # call operations
    python_eval,
    lambda_,
}

```
