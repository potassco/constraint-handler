## Information

This file describes the ASP fact format. These facts declare values, offer
candidate values, provide defaults, and state constraints. They are intended to
be facts.

Operator meanings are shared across input formats; see
[Operator Semantics](../OperatorSemantics.md).

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
2. Operators
   - `neg/1` (the logical `not` operator)
   - `and/2`
   - `or/2`
   - `eq/2`
     - QUESTIONS: Who implements this? Is this shared for all constructs?
       Extensional vs intensional vs both?
3. Declarations

#### Integer

1. Values
   - `val(int,<n>)` $\\mathtt{<n>}\\in\\mathbf{Z}$
2. Operators
   - `add/2`
   - `mul/2`
   - `geq/2`
   - `ge/2`
   - `leq/2`
   - `le/2`
   - `eq/2`
3. Declarations

#### Floats

1. Values
   - `val(float,"<n>")` $\\mathtt{<n>}\\in\\mathbf{R}$
2. Operators
   - `add/2`
   - `mul/2`
   - `geq/2`
   - `ge/2`?
   - `leq/2`
   - `le/2`?
   - `eq/2`?
3. Declarations

#### Strings

1. Values
   - `val(string,<w>)` `<w>` is a gringo string
2. Operators
   - `concat/2`
   - `trunc/2`
   - `substring/3`
3. Declarations

#### Python

1. Values
   - Alternatives:
     - `val(python,none)` or `val(python,<w>)` `<w>` is a gringo string or
     - no inherent values, return values are mapped into other constructs'
       values
2. Operators
   - `python_eval/2`
     - `python_eval("4 if x>4 else 2",((x,<expression>),(y,<expression>)))`
   - `python_execute/2`
     - `python_execute("x=4\ny=-x",y)`
3. Declarations

#### Sets

1. Values
   - Alternatives:
     - `val(set,<normalized expression gringo tuple>)` eg
       `val(set,(1,3,(5,6)))`
     - `val(set,set)` plus `set_include(<set_name>,<expression>)`
     - `val(set,<normalized expression tuple>)` eg
       `val(set,(1,3,(5,6)))` plus
       `set_include(<set_name>,<expression>)`
2. Operators
   - `set_make/n` (variadic: `n` elements)
   - `union/2`
   - `intersection/2`
   - `in/2`
   - `subset/2`
   - `superset/2`
3. Declarations
   - `set_choose`


#### Tuples

1. Values
   - `(val(int,1),val(float,"2.1"))`, `(val(int,1),)` (one element), `()` (empty)
2. Operators
   - `make_tuple/n` (variadic: `n` elements)
   - `tuple_index/2` (tuple and zero-based integer index)
   - `length/1`
   - `eq/2`
   - `neq/2`
3. Declarations

### Clingo-valid examples

The following are ground Clingo facts. The outer `example/2` predicate is only
for grouping examples; its second argument is the expression term. Operator
names are function symbols, so `not` cannot be used directly as one: it is
written as `neg` here. Clingo has integer numbers but no native
floating-point literals; the quoted decimal below is a string payload that an
input decoder must interpret as a float.

```prolog
% Values and expression forms
example(boolean_value, val(bool,true)).
example(integer_value, val(int,-3)).
example(float_value, val(float,"2.5")).
example(string_value, val(string,"hello")).
example(python_value, val(python,"payload")).
example(set_value, val(set,(val(int,1),val(int,2)))).
example(variable, variable(item)).
example(tuple_expression, (val(int,1),val(string,"one"))).
example(tuple_single, (val(int,1),)).
example(tuple_empty, ()).
example(tuple_nested, (val(int,1),(val(int,2),val(int,3)))).

% Tuple operators; index is 0-based
example(tuple_make, make_tuple(val(int,1),val(string,"one"),val(bool,true))).
example(tuple_index, tuple_index((val(int,1),val(string,"one")),val(int,1))).
example(tuple_length, length((val(int,1),val(string,"one")))).
example(tuple_eq, eq((val(int,1),val(int,2)),(val(int,1),val(int,2)))).
example(tuple_neq, neq((val(int,1),val(int,2)),(val(int,1),val(int,3)))).

% Boolean logic and shared equality
example(boolean_not, neg(val(bool,true))).
example(boolean_and, and(val(bool,true),val(bool,false))).
example(boolean_or, or(val(bool,true),val(bool,false))).
example(boolean_eq, eq(val(bool,true),val(bool,true))).

% Integer arithmetic and comparisons
example(integer_add, add(val(int,2),val(int,3))).
example(integer_mul, mul(val(int,2),val(int,3))).
example(integer_geq, geq(val(int,3),val(int,2))).
example(integer_ge, ge(val(int,3),val(int,2))).
example(integer_leq, leq(val(int,2),val(int,3))).
example(integer_le, le(val(int,2),val(int,3))).
example(integer_eq, eq(val(int,2),val(int,2))).

% Float-tagged arithmetic and comparisons
example(float_add, add(val(float,"1.5"),val(float,"2.0"))).
example(float_mul, mul(val(float,"1.5"),val(float,"2.0"))).
example(float_geq, geq(val(float,"2.0"),val(float,"1.5"))).
example(float_ge, ge(val(float,"2.0"),val(float,"1.5"))).
example(float_leq, leq(val(float,"1.5"),val(float,"2.0"))).
example(float_le, le(val(float,"1.5"),val(float,"2.0"))).
example(float_eq, eq(val(float,"1.5"),val(float,"1.5"))).

% String operators
example(string_concat, concat(val(string,"hello "),val(string,"world"))).
example(string_trunc, trunc(val(string,"constraint"),val(int,5))).
example(string_substring, substring(val(string,"constraint"),val(int,1),val(int,3))).

% Python operators; argument names are symbolic terms, not ASP variables
example(python_eval, python_eval(val(python,"4 if x>4 else 2"),((x,val(int,5)),(y,val(int,2))))).
example(python_execute, python_execute(val(python,"x=4\ny=-x"),y)).
example(python_eval, python_eval(val(string,"4 if x>4 else 2"),((x,val(int,5)),(y,val(int,2))))).
example(python_execute, python_execute(val(string,"x=4\ny=-x"),y)).

% Set operators
example(set_make, set_make(val(int,1),val(int,2))).
example(set_union, union(set_make(val(int,1)),set_make(val(int,2)))).
example(set_intersection, intersection(set_make(val(int,1),val(int,2)),set_make(val(int,2),val(int,3)))).
example(set_in, in(val(int,1),set_make(val(int,1),val(int,2)))).
example(set_subset, subset(set_make(val(int,1)),set_make(val(int,1),val(int,2)))).
example(set_superset, superset(set_make(val(int,1),val(int,2)),set_make(val(int,1)))).

% Base declarations and a condition represented by (expression, expected value)
define(variable(total),add(val(int,2),val(int,3))).
define(variable(conditional),val(int,1),(eq(variable(enabled),val(bool,true)),val(bool,true))).
choose(variable(choice),val(int,1)).
default_to(variable(fallback),val(string,"blue"),1).
default_to(variable(conditional_fallback),val(int,0),1,(eq(variable(enabled),val(bool,true)),val(bool,true))).
ensure(eq(variable(choice),val(int,1)),val(bool,true)).
check(geq(variable(total),val(int,0)),val(bool,true)).
minimize(variable(total),1).
maximize(variable(choice),2,(eq(variable(enabled),val(bool,true)),val(bool,true))).
set_choose(variable(labels),val(string,"urgent")).

% A condition over tuples of variables and corresponding value tuples
example(tuple_condition,((variable(x),variable(enabled)),((val(int,1),val(bool,true)),(val(int,2),val(bool,false))))).
```

### Expressions

```
<variable> ::=
  variable(<name>)
<expression> ::=
    | <value>
    | <variable>
    | <operator>(<expression>_1,..,<expression>_n)
    | expressiontuple
<expressiontuple> ::=
    | (expressionlist)
    | ()
<expressionlist> ::=
    | expression, expressionlist
    | expression
```

A one-element tuple needs a trailing comma, `(<expression>,)`, because
`(<expression>)` is only parenthesized grouping.

where `<name>` is a basic gringo term, and `<value>` is a value, and
`<operator>` an operator of any construct with `n` being its arity.

### Base declarations

1. `define(<variable>,<expression>(,<condition>))`
2. `choose(<variable>,<expression>(,<condition>))`
3. `default_to(<variable>,<expression>(,<priority>)(,<condition>))`
4. `ensure(<expression>,<value>(,<condition>))`
5. `check(<expression>,<value>(,<condition>))`
6. `minimize(<weight_expression>,(<priority>)(,<condition>))`
7. `maximize(<weight_expression>,(<priority>)(,<condition>))`

What is a `<condition>`?

- `(<expression>,<value>)`
- `((<variable>_1,..,<variable>_n),((<value>_11,..,<value>_1n),..,(<value>_m1,..,<value>_mn)))`
