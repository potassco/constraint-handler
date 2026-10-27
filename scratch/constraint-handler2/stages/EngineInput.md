## Information

The engine input consists of shared declaration facts from
[SharedEngineInput](SharedEngineInput.md), expression terms, and the assignments
produced by [Dispatching](Dispatching.md). It is generated after splitting and
Python conversion, without evaluating any expression.

## ASP Format

```asp
expr(expr_id, expr).
engine(native, expr_id).
engine(complex, expr_id).
engine(propagator, expr_id).
```

For each stored expression ID there is exactly one `expr/2` fact and exactly one
`engine/2` fact. The latter uses the engine chosen by dispatch, not all three
signatures shown above. IDs are emitted in ascending order. The root's engine
does not filter its expression or the shared declarations out of the fact base.

### Expression Terms

| Internal expression | ASP term |
| --- | --- |
| Boolean literal | `boolean(true)` or `boolean(false)` |
| Integer literal | `integer(value)` |
| Real literal | `real("repr")` |
| String literal | `string("value")` |
| None literal | `none` |
| Variable reference | `variable("name")` |
| Tuple expression | `tuple((element_terms))` |
| Set expression | `set((element_terms))` |
| Operation | `operation(operator,(argument_terms))` |
| Trusted Python descriptor | `python("source")` |

Parenthesized lists in this table are ASP tuples: `()` for zero elements,
`(term,)` for one, and `(first,second)` for two. Operations use the `Operator`
enum's value as an unquoted constant, including `if_` and `lambda_` where
applicable. Dispatch rejects unconverted lambda applications and descriptors;
the exporter also rejects lambda descriptors with `TypeError`.

Scalar tags preserve the distinction between booleans, integers, reals, and
strings. Reals use Python's `repr(float)` inside an ASP string because Clingo
does not have floating-point literals. This preserves `1.0` versus integer `1`
and negative zero. It also retains non-finite representations without interpreting
them. Real arithmetic is not implemented by serialization.

Collections and operation arguments are encoded recursively, in place, without
allocating more expression IDs. Tuple and argument order is retained. Set
elements are sorted by Clingo's symbol ordering for deterministic output.
Structural coefficient/term pairs in `linear_integer` are ordinary tuple terms.
The same applies to `linear_comparison`, whose first argument is a typed string
relation. A flat native comparison emits `linear_comparison_relation(Id,
string(Relation))`, indexed `linear_integer_term/4`, and
`linear_comparison_base(Id, Base)`, where `Base = offset + sum(ci * min(D(xi)))`.
It shares sorted `order_min/2` and gap-aware `order_next/3` parameter facts with
native sums. Both complementary Boolean outcomes compare the weighted aggregate
directly with `-Base`, guarded by integer values for every input. Missing inputs
produce neither outcome. No numeric total or result-domain assignment aggregate
is emitted. Empty input domains suppress the base; constant-only forms are
evaluated against an empty aggregate. Non-simple comparisons use normal
cost-based splitting and Python lowering rather than forced native execution.
Python source is retained as data, never executed by the exporter or the empty
native encoding. No domains or static type facts are emitted in this first step.

### Example

Given a store with `choose(x, 1, label="input")` and
`define(y, add(x, 2), label="derived")`, the fact base is:

```asp
variable_choose("x",0,1,"input").
variable_define("y",2,3,"derived").
expr(0,integer(1)).
engine(native,0).
expr(1,boolean(true)).
engine(native,1).
expr(2,operation(add,(variable("x"),integer(2)))).
engine(native,2).
expr(3,boolean(true)).
engine(native,3).
```

## Python Datastructure

The public `asp_facts(store, engines)` function returns an immutable tuple of
`clingo.Symbol` facts. `PreparedProblem.engines` retains dispatch assignments,
and the `PreparedProblem.asp_facts` property builds the facts on demand from
the prepared store and dispatch assignments. Facts are neither constructor
input nor cached state. See
[Computation](Computation.md) for grounding and solving.
