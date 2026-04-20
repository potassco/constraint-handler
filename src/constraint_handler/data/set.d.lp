%*! set_declare(Label, Name)

Declares a set with the given name.

The declaration introduces a set-valued variable. Individual elements can then
be added through [set_assign/2] or made optional through [set_baseDomain/2].

Args:
    - Label: The optional [Label] attached to the declaration.
    - Name: The name of the set.
*%

%*! set_declare(Name)

Shorthand for [set_declare/2] using an anonymous label.

Args:
    - Name: The name of the set.
*%

%*! set_assign(Label, Name, Expression)

Adds one expression result as an element to a set.

Args:
    - Label: The optional [Label] attached to the assignment.
    - Name: The name of the set.
    - Expression: The [Expression] whose valuation is inserted into the set.
*%

%*! set_assign(Name, Expression)

Shorthand for [set_assign/3] using an anonymous label.

Args:
    - Name: The name of the set.
    - Expression: The [Expression] whose valuation is inserted into the set.
*%

%*! set_baseDomain(Label, Name, Expression)

Adds one candidate element to the base domain of a set.

Each candidate introduced through this predicate may be chosen or omitted by the
solver independently.

Args:
    - Label: The optional [Label] attached to the base-domain declaration.
    - Name: The name of the set.
    - Expression: The candidate [Expression] for the set.
*%

%*! set_baseDomain(Name, Expression)

Shorthand for [set_baseDomain/3] using an anonymous label.

Args:
    - Name: The name of the set.
    - Expression: The candidate [Expression] for the set.
*%

%*! set_value(Name, Value)

One concrete element contained in a set.

Args:
    - Name: The name of the set.
    - Value: A value contained in the set.
*%
