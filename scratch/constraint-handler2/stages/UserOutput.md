## Output Predicates

### `value/2`

`value(Name, Value)` reports a variable's value in the current model. `Name`
is the variable's name, and `Value` is its assigned value.

```prolog
define(variable(total), add(val(int,2), val(int,3))).
```

The output is:

```prolog
value(total,val(int,5))
```

### `defined/1`

`defined(Name)` indicates that the variable named `Name` is defined in the
current model. No `defined(Name)` atom is output for a variable that is not
defined in that model.

```prolog
define(variable(total), add(val(int,2), val(int,3))).
define(variable(double_total), mul(variable(total), val(int,2))).
```

Both variables have values, so the output includes:

```prolog
defined(total)
defined(double_total)
```

A variable can also be defined only when a condition holds:

```prolog
define(variable(enabled), val(bool,false)).
define(
    variable(answer),
    val(int,42),
    (eq(variable(enabled), val(bool,true)), val(bool,true))
).
```

Here `answer` is not defined because `enabled` is false. The output contains
`defined(enabled)`, but not `defined(answer)`.

## TODO: Questions about `value/2` and `defined/1`

- Is `value(Name, Value)` always output for a defined variable, including when
  its value comes from the propagator?
- Are `defined(Name)` and `value(Name, Value)` guaranteed to occur together in
  every model?
- Can a variable be known to be defined without having a specific value? If
  so, how should that case be represented in the output?
