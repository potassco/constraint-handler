## Information

This file should give an overview about a public python interface for the
constraint handler. Objects should be connected in tree like structures to
describe higher level concepts. For example:

```python
# Example of representing a sequence of statements as a tree-like structure
# The object tree below represents this Python code:
#
# x = a * 2
# if a == 0:
#     y = x
# else:
#     y = x + 2
#
root = Seq2(
    fst=Assign(
        var="x",
        expr=Operation(
            op=ArithmeticOperator.mult,
            args=(Variable("a"), Val(BaseType.int, 2))
        )
    ),
    snd=If(
        cond=Operation(
            op=EqOperator.eq,
            args=(Variable("a"), Val(BaseType.int, 0))
        ),
        then=Assign(var="y", expr=Variable("x")),
        else_=Assign(
            var="y",
            expr=Operation(
                op=ArithmeticOperator.add,
                args=(Variable("x"), Val(BaseType.int, 2))
            )
        )
    )
)
```

## ASP Format

## Python Datastructure

```python
# A FailIntegrity exception aborts statement evaluation when an assertion fails.
#
FailIntegrity()

# EqOperator is an enum for equality comparisons.
#
enum EqOperator {
    eq,
    neq
}

# StringOperator is an enum for string operations.
#
enum StringOperator {
    concat,
    length
}

# OtherOperator is an enum for generic extrema operations.
#
enum OtherOperator {
    max,
    min,
    length
}

# ConditionalOperator is an enum whose members are used as operator values.
#
enum ConditionalOperator {
    getOrElse,
    IF,
    hasValue
}

# ArithmeticOperator is an enum whose members are used as numeric operator values.
#
enum ArithmeticOperator {
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
    int_from_float
}

# LogicOperator is an enum whose members are used as Boolean and three-valued logic operator values.
#
enum LogicOperator {
    conj,
    disj,
    ite,
    leqv,
    limp,
    lnot,
    lxor,
    snot,
    wnot
}

# SetOperator is an enum whose members are used for constructing and querying sets.
#
enum SetOperator {
    cardinality,
    set_make,
    set_isin,
    set_notin,
    union,
    inter,
    diff,
    subset,
    set_fold
}

# MultimapOperator is an enum whose members are used for constructing and querying multimaps.
#
enum MultimapOperator {
    find,
    find2,
    multimap_isin,
    multimap_make,
    multimap_fold,
    multimap_fold_i,
    countKeys,
    countEntries,
    sumIntEntries,
    maxEntries,
    minEntries
}

# BaseType is an enum naming the scalar and collection types understood by the evaluator.
#
enum BaseType {
    int,
    float,
    string,
    symbol,
    bool,
    none,
    function,
    multimap,
    set
}
# Example: Val(BaseType.int, 2) constructs an integer literal.

# The expression.constant alias lists values that can appear as literal arguments.
#
constant = bool | float | int | str | None | clingo.Symbol

# The expression.Operator alias lists all operator values accepted by Operation and Evaluate.
#
Operator = ArithmeticOperator | EqOperator | LogicOperator | StringOperator | MultimapOperator | SetOperator | OtherOperator | ConditionalOperator | Python | PythonExtract

# Expr is the recursive type of expressions accepted by the evaluator.
#
Expr = Bad | Variable | Operation | Python | Val | Ref | Lambda | frozenset[Expr] | tuple[Expr, ...]

# ReducedExpr is the type of an expression after evaluation and reduction.
#
ReducedExpr = Bad | Val | Ref | frozenset[ReducedExpr] | tuple[ReducedExpr, ...]

# Stmt is the union of statement constructors executed by the evaluator.
#
Stmt = Assert | Assign | If | Noop | Statement_python | Seq2

# Domain is the union of domain marker constructors.
#
Domain = Definition | BoolDomain | FromFacts | Open | Set | Multimap

# ImmutableList stores an immutable sequence used when converting lists between Python and clingo.
#
ImmutableList(values: Iterable[Any])
# Example: ImmutableList((Variable("x"), Val(BaseType.int, 2))) constructs an immutable argument list.

# A Val stores a typed literal value in an expression.
# For example, the integer literal 2 is represented as Val(BaseType.int, 2).
#
Val(type_: BaseType | clingo.Symbol, value: bool | float | int | str | None | clingo.Symbol)

# A Ref stores a typed reference to a value represented by a clingo symbol.
#
Ref(type_: BaseType | clingo.Symbol, value: bool | float | int | str | None | clingo.Symbol)
# Example: Ref(BaseType.int, clingo.Function("x")).

# A Variable stores the name of a variable used by an expression.
# For example, x in x + 2 is represented as Variable(x).
#
Variable(arg: bool | float | int | str | None | clingo.Symbol)

# An Operation stores an operator and its argument expressions.
# For example, x + 2 is represented as Operation(add, (Variable(x), Val(int, 2))).
#
Operation(op: Operator | Variable | Lambda, args: ImmutableList[Expr])
# Example: Operation(ArithmeticOperator.add, ImmutableList((Variable("x"), Val(BaseType.int, 2)))).

# A Lambda stores parameter names and an expression body.
#
Lambda(vars: ImmutableList[clingo.Symbol], expr: Expr)
# Example: Lambda(ImmutableList((clingo.Function("x"),)), Variable("x")).

# A Python stores a Python expression that the evaluator executes.
#
Python(fn: str)
# Example: Python("math.sqrt(x)") evaluates a Python expression using x.

# A PythonExtract stores a Python statement and an expression evaluated after that statement.
#
PythonExtract(stmt: str, expr: str)
# Example: PythonExtract("y = x + 1", "y * 2").

# A CustomOperator stores the clingo symbol naming a custom operator.
#
CustomOperator(name: clingo.Symbol)

# An Assert requires its expression to evaluate to true.
#
Assert(expr: Expr)
# Example: Assert(Operation(LogicOperator.conj, ImmutableList((Variable("ready"), Variable("enabled"))))).

# An Assign evaluates an expression and stores the result in a local variable.
#
def Assign(var: constant, expr: Expr)
# Example: Assign("y", Operation(ArithmeticOperator.add, ImmutableList((Variable("x"), Val(BaseType.int, 2))))).

# An If evaluates one of two statements according to its condition.
#
If(cond: Expr, then: Stmt, else_: Stmt)
# Example: If(Variable("ok"), Assign("y", Val(BaseType.int, 1)), Noop()).

# A Noop represents a statement with no effect.
#
Noop()

# A Statement_python stores Python code executed as a statement.
#
Statement_python(code: str)
# Example: Statement_python("total = total + item").

# A Seq2 stores two statements executed from left to right.
#
Seq2(fst: Stmt, snd: Stmt)
# Example: Seq2(Assign("x", Val(BaseType.int, 2)), Assert(Variable("x"))).

# An EvalResult stores an evaluated value together with evaluator warnings or errors.
#
EvalResult(value: Any, errors: tuple[tuple[warning.Kind, str], ...])
# Example: EvalResult(4, ()) is a successful evaluation.

# A Variable_declare declares a variable and its domain.
#
Variable_declare(label: constant, name: constant, domain: Domain)
# Example: Variable_declare("input", "x", Definition()).

# A Variable_define assigns an expression to a variable.
#
Variable_define(label: constant, name: constant, value: Expr)
# Example: Variable_define("input", "x", Val(BaseType.int, 2)).

# A Variable_default assigns a conditional default value with a priority.
#
Variable_default(label: constant, name: constant, value: Expr, condition: Expr, priority: constant)
# Example: Variable_default("defaults", "x", Val(BaseType.int, 0), Variable("missing"), 1).

# A Variable_domain assigns an expression describing a variable domain.
#
Variable_domain(label: constant, name: constant, value: Expr)
# Example: Variable_domain("domain", "x", Operation(SetOperator.set_make, ImmutableList((Val(BaseType.int, 1), Val(BaseType.int, 2))))).

# A Bool_evaluate requests evaluation of a Boolean expression.
#
Bool_evaluate(label: constant, expr: Expr)
# Example: Bool_evaluate("check", Operation(EqOperator.eq, ImmutableList((Variable("x"), Val(BaseType.int, 2))))).

# A Bool_evaluated stores the reduced value of a Boolean expression.
#
Bool_evaluated(expr: Expr, value: ReducedExpr)

# A Set_assign adds an expression as a member of a named set.
#
Set_assign(label: constant, name: constant, member: Expr)
# Example: Set_assign("items", "selected", Variable("x")).

# A Set_baseDomain defines the base domain expression of a set.
#
Set_baseDomain(label: constant, name: constant, value: Expr)
# Example: Set_baseDomain("items", "selected", Variable("available")).

# A Set_value stores one reduced value belonging to a set.
#
Set_value(name: constant, elt: ReducedExpr)
# Example: Set_value("selected", Val(BaseType.int, 2)).

# A Multimap_assign adds a key/value expression pair to a named multimap.
#
Multimap_assign(label: constant, name: constant, key: Expr, val: Expr)
# Example: Multimap_assign("costs", "by_item", Variable("item"), Variable("cost")).

# A Multimap_value stores one reduced key and one reduced multimap value.
#
Multimap_value(name: constant, key: ReducedExpr, cst: ReducedExpr)
# Example: Multimap_value("by_item", Val(BaseType.string, "pen"), Val(BaseType.int, 3)).

# An Execution_declare declares a named statement and its input and output variables.
#
Execution_declare(label: constant, name: constant, body: Stmt, inputs_vars: ImmutableList[constant], outputs_vars: ImmutableList[constant])
# Example: Execution_declare("jobs", "compute", Assign("y", Variable("x")), ImmutableList(("x",)), ImmutableList(("y",))).

# An Execution_run requests execution of a declared statement.
#
Execution_run(label: constant, name: constant)
# Example: Execution_run("jobs", "compute").

# An Optimize_maximizeSum contributes an expression to an optimization objective.
#
Optimize_maximizeSum(label: constant, value: Expr, id: constant, priority: constant)
# Example: Optimize_maximizeSum("profit", Variable("value"), "item1", 1).

# An Optimize_precision configures the precision used by optimization.
#
Optimize_precision(value: Expr, priority: constant)
# Example: Optimize_precision(Val(BaseType.int, 100), 1).

# An Optimize_modelValue stores an optimization value read from a model.
#
Optimize_modelValue(label: constant, priority: constant, total: constant)

# An Optimize_value stores an optimization value produced by the engine.
#
Optimize_value(label: constant, priority: constant, total: constant)

# A Preference_maximizeScore selects score maximization for preferences.
#
Preference_maximizeScore()

# A Preference_holds contributes a weighted preference expression.
#
Preference_holds(label: constant, value: Expr, factor: int)
# Example: Preference_holds("preferred", Variable("x"), 10).

# A Preference_variableValue contributes a weighted preference for a variable value.
#
Preference_variableValue(label: constant, variable: constant, value: Expr, factor: int)
# Example: Preference_variableValue("preferred", "x", Val(BaseType.string, "blue"), 10).

# A Preference_score stores the calculated preference score.
#
Preference_score(score: int)
# Example: Preference_score(10).

# An Ensure requires an expression to hold in the current model.
#
Ensure(label: constant, expr: Expr)
# Example: Ensure("required", Variable("valid")).

# A Value stores a named reduced value exposed by the engine.
#
Value(name: constant, val: ReducedExpr)
# Example: Value("x", Val(BaseType.int, 2)).

# An Evaluate requests application of an operator to argument expressions.
#
Evaluate(label: constant, operator: Operator | Variable, args: ImmutableList[Expr])
# Example: Evaluate("sum", ArithmeticOperator.add, ImmutableList((Val(BaseType.int, 1), Val(BaseType.int, 2)))).

# An Evaluated stores the reduced result of an operator application.
#
Evaluated(name: Operator, expr: ImmutableList[Expr], value: ReducedExpr)
# Example: Evaluated(ArithmeticOperator.add, ImmutableList((Val(BaseType.int, 1), Val(BaseType.int, 2))), Val(BaseType.int, 3)).

# A Definition, FromFacts, BoolDomain, Open, Set, or Multimap is a domain marker.
#
Definition()
FromFacts()
BoolDomain()
Open()
Set()
Multimap()
# Example: Variable_declare("facts", "x", FromFacts()) uses facts as a domain.
```

## TODO

- list above needs a huge cleaning, this is not a public interface yet
- why is ImmutableList a datatype, why not tuple
