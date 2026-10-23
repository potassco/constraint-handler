## Information

This file describes the ASP fact format. These facts declare values, offer
candidate values, provide defaults, and state constraints. They are intended to
be facts.

## ASP Format

### Construct library

Here, we define different constructs that can be included into
constraint-handler reasoning. Every construct has values, operators and
optional declarations. Constructs might depend on or intersect each other, for
instance, equality, sets, and other predicate-like operators that return
boolean. Values are meant as the fundamental domain constants that occur in the
ultimate assignment.

Unless otherwise specified, all terms are Gringo symbols, ie constants,
numbers, strings, tuples, functions.

#### Boolean logic

1. Values
   - `val(bool,true)` `val(bool, false)`
1. Operators
   - `not`
     - arity: 1
     - definition: `not(val(bool,true))` = `val(bool,false)`;
       `not(val(bool,false))` = `val(bool,true)`
   - `and`
   - `or`
   - `eq`
     - QUESTIONS: Who implements this? Is this shared for all constructs?
       Extensional vs intensional vs both?
1. Declarations

#### Integer

1. Values
   - `val(int,<n>)` $\\mathtt{<n>}\\in\\mathbf{Z}$
1. Operators
   - `add`
     - arity: 2
     - definition:
       - `add(val(int,<n_1>),val(int,<n_2>))` = `val(int,<n_1>+<n_2>)`
   - `mul`
   - `geq`
   - `ge`
   - `leq`
   - `le`
   - `eq`?
1. Declarations

#### Floats

1. Values
   - `val(float,<n>)` $\\mathtt{<n>}\\in\\mathbf{R}$
1. Operators
   - `add`
   - `mul`
   - `geq`
   - `ge`?
   - `leq`
   - `le`?
   - `eq`?
1. Declarations

#### Strings

1. Values
   - `val(string,<w>)` `<w>` is a gringo string
1. Operators
   - `concat`
   - `trunc`
   - `substring`
1. Declarations

#### Python

1. Values
   - Alternatives:
     - `val(python,none)` or `val(python,<w>)` `<w>` is a gringo string or
     - no inherent values, return values are mapped into other constructs'
       values
1. Operators
   - `python_eval`
     - `python_eval("4 if x>4 else 2",((x,<expression>),(y,<expression>)))`
   - `python_execute`
     - `python_execute("x=4\n y=-x",y)`
1. Declarations

#### Sets

1. Values
   - Alternatives:
     - `val(set,<normalized expression gringo tuple>)` eg
       `val(set,(1,3,variable(v),(5,6)))`
     - `val(set,set)` plus `set_include(<set_name>,<expression>)`
     - `val(set,<normalized expression tuple>)` eg
       `val(set,(1,3,variable(v),(5,6)))` plus
       `set_include(<set_name>,<expression>)`
1. Operators
   - `set_make`
   - `union`
   - `intersection`
   - `in`
   - `subset`
   - `superset`
1. Declarations
   - `set_choose`

#### Tuples

1. Values
   - `val(tuple,(<value>_1,..<value>_n))`
1. Operators
   - `make_tuple`?
1. Declarations

### Expressions

```
<variable> ::=
  variable(<name>)
<expression> ::=
    | <value>
    | <variable>
    | <operator>(<expression>_1,..,<expression>_n)
```

where `<name>` is a basic gringo term, and `<value>` is a value, and
`<operator>` an operator of any construct.

### Base declarations

1. `define(<variable>,<expression>(,<condition>))`
1. `choose(<variable>,<expression>(,<condition>))`
1. `default_to(<variable>,<expression>(,<priority>)(,<condition>))`
1. `ensure(<expression>,<value>(,<condition>))`
1. `check(<expression>,<value>(,<condition>))`
1. `prefer(<expression>,<value>,(<priority>,<weight>)(,<condition>))`

What is a `<condition>`?

- `(<expression>,<value>)`
- `((<variable>_1,..,<variable>_n),((<value>_11,..,<value>_1n),..,(<value>_m1,..,<value>_mn)))`
