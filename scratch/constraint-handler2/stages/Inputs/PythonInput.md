## Information

This file describes the caller-facing Python interface and expression model for
adding input to a `ConstraintStore`. Input is declarative: variables are
declared and defined with expressions, rather than represented as executable
statements. A possible internal storage representation is described in
[InternalInput](InternalInput.md).

```python
from python_input import Operation, Operator, VariableRef

store = ConstraintStore()
store.variable_declare(
    VariableRef("x"),
    VariableKind.regular,
    (1, 2)
)
store.variable_define(
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
# VariableKind identifies a variable's value shape.
#
enum VariableKind {
    regular,
    set,
    multi_set
}

# A VariableRef stores the name of a variable used by an expression.
# For example, x in x + 2 is represented by VariableRef(x).
#
VariableRef(name: str)

```

### ConstraintStore Methods

```python

class ConstraintStore:
    # variable_declare declares a variable, its kind, and its candidate domain.
    # A domain of None means the variable is open; otherwise its expressions are candidate values.
    #
    def variable_declare(self, name: VariableRef, kind: VariableKind, domain: tuple[Expr, ...] | None, label: str = LABEL_ANONYMOUS): ...

    # variable_define defines a variable's value with an expression.
    #
    def variable_define(self, name: VariableRef, value: Expr, label: str = LABEL_ANONYMOUS): ...

    # variable_default defines a conditional default value with a priority.
    #
    def variable_default(self, name: VariableRef, value: Expr, condition: Expr = expression.TRUE, priority: int = 0, label: str = LABEL_ANONYMOUS): ...

    # actual constraints
    # check(x/0 > 9). holds and ensure(x/0 > 9) does not hold
    def ensure(self, expr: Expr, label: str = LABEL_ANONYMOUS): ...
    def check(self, expr: Expr, label: str = LABEL_ANONYMOUS): ...

# Examples
from python_input import Operation, Operator, VariableRef

store.variable_declare(VariableRef("x"), VariableKind.regular, (1, 2), "input")
store.variable_define(VariableRef("x"), 2, "input")
store.variable_default(
    VariableRef("x"),
    0,
    Operation(Operator.eq, (VariableRef("x"), 1)),
    "1",
    "defaults",
)


```

### Expressions

```python
# These expression types belong to the python_input namespace.
#
Expr = VariableRef | Value | Set | Tuple | MultiDict | Operation

# Scalar values use Python base types at the user-facing boundary.
#
Value = bool | float | int | str | None

# Collections are expression forms, not scalar values.
#
Set = frozenset[Expr]
Tuple = tuple[Expr, ...]
MultiDict = dict[Expr, frozenset[Expr]]

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

# Python stores a Python expression that the evaluator executes.
#
Python(fn: str)
# Example: Python("math.sqrt(x)") evaluates a Python expression using x.


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
    int_div,
    float_div,
    pow,
    leq,
    lt,
    geq,
    gt,
    float_from_int,
    int_from_float,

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

    # Multimap construction and queries
    find,
    find2,
    multimap_isin,
    multimap_make,
    multimap_fold,
    multimap_fold_i,
    count_keys,
    count_entries,
    sum_int_entries,
    max_entries,
    min_entries,

    # call operations
    python_eval,
    lambda_,
}

```
