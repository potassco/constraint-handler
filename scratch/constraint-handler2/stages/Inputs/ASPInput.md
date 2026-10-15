## Information

This file describes the ASP fact format. These facts declare values,
offer candidate values, provide defaults, and state constraints. They are
intended to be heads of ASP rules; ordinary rule bodies can condition when a
statement applies.

## ASP Format

### Value expressions

Expressions are terms. Scalar values carry an explicit type, variable
references use `variable/1`, and operators are represented by terms named for
the operator:

```prolog
val(int,4)
variable(x)
add(val(int,2),val(int,2))
eq(variable(x),val(int,4))
```

The examples also use `naf/1` and `neg/1` for distinct negation expressions.
Operator terms can be nested to form larger expressions.

### Statements

The statement predicates are:

| Form | Meaning |
| --- | --- |
| `singleton_assign(name,expression)` and `set_assign(name,expression)` | Assign an expression as the value of a singleton or as a set element. |
| `multimap_assign(name,key,expression)` | Assigns an expression for a key in the named multimap. |
| `singleton_choice(name,expression)` and `set_choice(name,expression)` | Offer an expression as a possible singleton value or set element. |
| `multimap_choice(name,key,expression)` | Offers an expression as a possible value for a multimap key. |
| `singleton_default(name,expression[,condition[,priority]])`, `set_default(name,expression[,condition[,priority]])`, `multimap_default(name,key,expression[,condition[,priority]])` | Provide a fallback expression, optionally guarded by a condition and ordered by priority. |
| `ensure(expression)` | Requires the expression to evaluate to `val(bool,true)`. |
| `default_mode(mode)` | Selects `basic`, `assign`, or `depends` default handling. The default mode is `assign`. |

The set forms have no key argument; multimap forms include a key. Assignment,
choice, default, and `ensure` statements occur in rule heads. For example, a rule body
can make a choice conditional, while a choice rule can make that justification
optional:

```prolog
singleton_choice(x,val(int,4)) :- a.
{ singleton_choice(x,val(int,5)) }.
```

## Python Datastructure

Use Clorm-compatible typed records for predicate atoms and expression terms.
The project converts these records to Clingo symbols using
`constraint_handler.myClorm.pytocl`; record names map to predicate names by
lowercasing the first letter. Thus `Singleton_assign` represents
`singleton_assign`, and `Val` represents `val`.

```python
from __future__ import annotations

from typing import NamedTuple

import clingo
import constraint_handler.myClorm as myClorm


class Val(NamedTuple):
	type: clingo.Symbol
	value: bool | int | float | str | None


class Variable(NamedTuple):
	name: clingo.Symbol


class Add(NamedTuple):
	left: Expr
	right: Expr


class Singleton_assign(NamedTuple):
	name: clingo.Symbol
	expression: Expr


type Expr = Val | Variable | Add


statement = Singleton_assign(
	clingo.Function("x"),
	Add(Val(clingo.Function("int"), 2), Val(clingo.Function("int"), 2)),
)
symbol = myClorm.pytocl(statement)
# singleton_assign(x,add(val(int,2),val(int,2)))
```

Define a corresponding record for each predicate or expression constructor
used by an input program. The full expression type must include every operator
and expression form used by that program. Names such as `x`, types such as
`int`, and operators such as `eq` are Clingo symbols; quoted ASP strings map
to Python `str` values.

## TODO

- Confirm the final signatures and semantics for set and multimap statements.
- Consider further language constructs like multiple check and ensure (former does not require proof latter does).
- Decide whether `default_mode` may be specified more than once per variable or expressions.
