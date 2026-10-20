## Information

This file describes the ASP fact format. These facts declare values, offer
candidate values, provide defaults, and state constraints. They are intended to
be facts.

## ASP Format

### Base declarations

1. `define(<variable>,<expression>(,<condition>))`
2. `choose(<variable>,<expression>(,<condition>))`
3. `default_to(<variable>,<expression>(,<priority>)(,<condition>))`
4. `ensure(<expression>,<value>(,<condition>))`
5. `check(<expression>,<value>(,<condition>))`
6. `prefer(<expression>,<value>,(<priority>,<weight>)(,<condition>))`

### Construct library

#### Boolean logic

1. Values
2. Operators
3. Declarations

#### Integer

1. Values
2. Operators
3. Declarations

#### Floats

1. Values
2. Operators
3. Declarations

#### Strings

1. Values
2. Operators
3. Declarations

#### Python

1. Values
2. Operators
3. Declarations

#### Sets

1. Values
2. Operators
3. Declarations

## TODO

- Confirm the final signatures and semantics for set and multimap statements.
- Consider further language constructs like multiple check and ensure (former
  does not require proof latter does).
- Decide whether `default_mode` may be specified more than once per variable or
  expressions.
